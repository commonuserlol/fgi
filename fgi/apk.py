import platform
import shutil
import subprocess
from pathlib import Path

from fgi.arguments import Arguments
from fgi.logger import Logger
from fgi.path import PathUtils


class APK:
    def __init__(self, arguments: Arguments, apkeditor_path: Path):
        self.is_split_apk = arguments.is_split_apk()
        self.should_delete = not arguments.no_cleanup
        self.path_utils = PathUtils(
            arguments.input, arguments.out, arguments.temp_root_path
        )
        self.apkeditor_path = apkeditor_path

    def _run_command_and_check(self, cmd: list[str]):
        try:
            Logger.debug(f"Running {cmd}")
            return subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode("utf8")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Command {cmd} returned non-zero exit status: {e.output.decode('utf8')}"
            )

    def merge(self):
        Logger.info("Merging split APKs...")
        self._run_command_and_check(
            [
                "java",
                "-jar",
                self.apkeditor_path,
                "m",
                "-i",
                self.path_utils.get_input_apk_path(),
                "-o",
                self.path_utils.get_merged_apk_path(),
            ]
        )
        self.path_utils.switch_input_to_merged()

    def decode(self):
        Logger.info(f"Decoding APK to {self.get_temp_path()}...")
        self._run_command_and_check(
            [
                "java",
                "-jar",
                self.apkeditor_path,
                "d",
                "-i",
                self.path_utils.get_input_apk_path(),
                "-o",
                self.get_temp_path(),
            ]
        )

    def build(self):
        Logger.info("Building APK...")
        self._run_command_and_check(
            [
                "java",
                "-jar",
                self.apkeditor_path,
                "b",
                "-i",
                self.get_temp_path(),
                "-o",
                self.path_utils.get_built_apk_path(),
            ]
        )

    def zipalign(self):
        Logger.info("Zipaligning APK...")
        self._run_command_and_check(
            [
                "zipalign",
                "-p",
                "4",
                self.path_utils.get_built_apk_path(),
                self.path_utils.get_zipaligned_apk_path(),
            ]
        )
        self.path_utils.get_built_apk_path().unlink()

    def generate_debug_key(self, key_path: Path):
        Logger.debug("Generating key...")
        self._run_command_and_check(
            [
                "keytool",
                "-genkey",
                "-v",
                "-keystore",
                key_path,
                "-storepass",
                "android",
                "-alias",
                "androiddebugkey",
                "-keypass",
                "android",
                "-keyalg",
                "RSA",
                "-keysize",
                "2048",
                "-validity",
                "10000",
                "-dname",
                "C=US, O=Android, CN=Android Debug",
            ]
        )

    def sign(self, key_path: Path):
        Logger.info("Signing APK...")
        # Move APK to track stage if any error
        shutil.move(
            self.path_utils.get_zipaligned_apk_path(),
            self.path_utils.get_signed_apk_path(),
        )

        apksigner_executable = "apksigner"

        if platform.system() == "Windows":
            apksigner_executable += ".bat"

        self._run_command_and_check(
            [
                apksigner_executable,
                "sign",
                "--ks",
                key_path,
                "--ks-pass",
                "pass:android",
                "--ks-key-alias",
                "androiddebugkey",
                self.path_utils.get_signed_apk_path(),
            ]
        )
        shutil.move(
            self.path_utils.get_signed_apk_path(), self.path_utils.get_out_apk_path()
        )  # XXX: assume that everything is ready

    def get_entry_activity(self):
        output = self._run_command_and_check(
            [
                "java",
                "-jar",
                self.apkeditor_path,
                "info",
                "-i",
                self.path_utils.get_input_apk_path(),
                "-activities",
            ]
        )
        if self.is_split_apk:
            # Now we can safely remove merged APK
            self.path_utils.get_merged_apk_path().unlink()
        entrypoints = output.strip().replace("activity-main=", "").replace('"', "")
        assert entrypoints is not None, "No entrypoint(s) found :("
        return entrypoints

    def get_temp_path(self) -> Path:
        return self.path_utils.get_temp_path()

    def __del__(self):
        if self.should_delete and self.get_temp_path().exists():
            shutil.rmtree(self.get_temp_path())
        if not self.get_temp_path().exists():
            return
        # GC everything if program died before GC in function
        self.path_utils.get_merged_apk_path().unlink(True)
        self.path_utils.get_built_apk_path().unlink(True)
        self.path_utils.get_zipaligned_apk_path().unlink(True)
        self.path_utils.get_signed_apk_path().unlink(True)
