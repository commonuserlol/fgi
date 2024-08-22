import platform
import shutil
import random
import string
from pathlib import Path
from fgi.arguments import Arguments
from fgi.loaders.base import BaseLoader
from fgi.loaders.split import SplitAPKLoader
from fgi.logger import Logger
from fgi.cmd import run_command_and_check


class APK:
    def __init__(self, apkeditor_path: Path, arguments: Arguments, loader: BaseLoader):
        self.apkeditor_path = apkeditor_path
        self.arguments = arguments
        self.loader = loader

        # Well, I could use @property but python will complain if I use lazy decorator
        self.temp_path = self.arguments.temp_root_path / "".join(random.choices(string.ascii_letters, k=12))

    @property
    def _built_apk_path(self):
        return self.arguments.temp_root_path / (self.loader.source.absolute().name + "-built")

    @property
    def _zipaligned_apk_path(self):
        return self.arguments.temp_root_path / (self.loader.source.absolute().name + "-zipaligned")

    @property
    def _signed_apk_path(self):
        return self.arguments.temp_root_path / (self.loader.source.absolute().name + "-signed")

    def decode(self):
        Logger.info(f"Decoding APK to {self.temp_path}...")
        _ = run_command_and_check(
            [
                "java",
                "-jar",
                self.apkeditor_path,
                "d",
                "-i",
                self.loader.output_path,
                "-o",
                self.temp_path,
            ]
        )

    def build(self):
        Logger.info("Building APK...")
        _ = run_command_and_check(
            [
                "java",
                "-jar",
                self.apkeditor_path,
                "b",
                "-i",
                self.temp_path,
                "-o",
                self._built_apk_path,
            ]
        )

    def zipalign(self):
        Logger.info("Zipaligning APK...")
        _ = run_command_and_check(
            [
                "zipalign",
                "-p",
                "4",
                self._built_apk_path,
                self._zipaligned_apk_path,
            ]
        )
        self._built_apk_path.unlink()

    def generate_debug_key(self, key_path: Path):
        Logger.debug("Generating key...")
        _ = run_command_and_check(
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
        shutil.move(self._zipaligned_apk_path, self._signed_apk_path)

        apksigner_executable = "apksigner"

        if platform.system() == "Windows":
            apksigner_executable += ".bat"

        _ = run_command_and_check(
            [
                apksigner_executable,
                "sign",
                "--ks",
                key_path,
                "--ks-pass",
                "pass:android",
                "--ks-key-alias",
                "androiddebugkey",
                self._signed_apk_path,
            ]
        )
        shutil.move(
            self._signed_apk_path,
            self.arguments.out,  # pyright: ignore[reportArgumentType]
        )  # XXX: assume that everything is ready

    def get_entry_activity(self):
        output = run_command_and_check(
            [
                "java",
                "-jar",
                self.apkeditor_path,
                "info",
                "-i",
                self.loader.output_path,
                "-activities",
            ]
        )
        if isinstance(self.loader, SplitAPKLoader):
            # Now we can safely remove merged APK
            self.loader.output_path.unlink()
        entrypoints = output.strip().replace("activity-main=", "").replace('"', "")
        assert entrypoints is not None, "No entrypoint(s) found :("
        return entrypoints

    def __del__(self):
        if not self.arguments.no_cleanup and self.temp_path.exists():
            shutil.rmtree(self.temp_path)
        # GC everything if program died before GC in function
        if isinstance(self.loader, SplitAPKLoader) and self.loader.merge_temp_path.exists():
            shutil.rmtree(self.loader.merge_temp_path)
        self._built_apk_path.unlink(True)
        self._zipaligned_apk_path.unlink(True)
        self._signed_apk_path.unlink(True)
