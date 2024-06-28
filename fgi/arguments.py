from typing import Any, Optional
from pathlib import Path
from dataclasses import dataclass
import json
import argparse
from fgi.constants import ARCHITECTURES


@dataclass
class Arguments:
    input: Path
    out: Path
    architectures: list[str]
    config_type: Optional[str]
    config_path: Optional[Path]
    script_path: Optional[Path]
    library_name: str
    script_name: str
    temp_root_path: Path
    no_cleanup: bool
    offline_mode: bool
    verbose: bool

    @staticmethod
    def create():
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-i", "--input", type=Path, required=True, help="Target APK file"
        )
        parser.add_argument(
            "-o", "--out", type=Path, help="Output APK file"
        )  # XXX: default value determined after arguments parsed
        parser.add_argument(
            "-a",
            "--architectures",
            nargs="*",
            choices=ARCHITECTURES.keys(),
            default=ARCHITECTURES.keys(),
            help="Target architecture(s) for frida-gadget",
        )

        parser.add_argument(
            "-t",
            "--config-type",
            type=str,
            choices=["listen", "connect", "script"],
            help="Target config type",
        )
        parser.add_argument("-c", "--config-path", type=Path, help="Custom config path")
        parser.add_argument("-l", "--script-path", type=Path, help="Script path")

        parser.add_argument(
            "-n",
            "--library-name",
            type=str,
            default="libfrida.so",
            help='frida-gadget library name, must have "lib" at start and "so" at end',
        )
        parser.add_argument(
            "-s",
            "--script-name",
            type=str,
            default="libscript.so",
            help='frida-gadget script name, must have "lib" at start and "so" at end',
        )

        parser.add_argument(
            "-r",
            "--temp-root-path",
            type=Path,
            default="/tmp",
            help="Root path where temporary directory will be created",
        )

        parser.add_argument(
            "--no-cleanup",
            action="store_true",
            help="Do not remove temporary directory (useful for debugging)",
        )
        parser.add_argument(
            "--offline-mode", action="store_true", help="Disable updates check for deps"
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Verbose logging (useful for debugging)",
        )

        args = parser.parse_args()
        return Arguments(
            args.input,
            args.out,
            args.architectures,
            args.config_type,
            args.config_path,
            args.script_path,
            args.library_name,
            args.script_name,
            args.temp_root_path,
            args.no_cleanup,
            args.offline_mode,
            args.verbose,
        )

    def validate(self):
        if not self.is_split_apk():  # XXX: Assume that split APKs always exists
            assert self.input.exists(), "Input APK doesn't exist"
        if self.out is None:
            if ".apk" not in self.input.name:
                self.out = Path.cwd() / (self.input.name + ".patched.apk")
            else:
                self.out = Path.cwd() / self.input.name.replace(".apk", ".patched.apk")
        assert (
            not self.out.exists()
        ), 'Out path is exist, delete, rename or specify manually via "-o"'
        assert self.out.name.endswith(".apk"), "Out filename must endswith .apk"
        assert self.is_builtin_config() or (
            self.config_path and not self.config_type
        ), 'Specify "config-type" or "config-path", both options aren\'t allowed'
        if self.is_script_required():
            assert self.script_path, 'Script is required when "config-type" equals "script" or config provided via "config-path" have "type": "script"'
            assert self.script_path.exists(), "Script doesn't exist"
        assert self.library_name.startswith("lib") and self.library_name.endswith(
            ".so"
        ), "Invalid name for frida library"
        assert self.script_name.startswith("lib") and self.script_name.endswith(
            ".so"
        ), "Invalid name for frida script"
        assert self.temp_root_path.exists(), "Root temp path doesn't exist"

    def is_builtin_config(self) -> bool:
        return not self.config_path and self.config_type

    def is_script_required(self) -> bool:
        if self.config_type == "script":
            return True
        if self.config_path:
            with open(self.config_path, "r", encoding="utf8") as f:
                config_dict: dict[str, dict[str, Any]] = json.load(f)
            interaction: dict[str, Any] = config_dict.get("interaction", False)
            assert interaction, '"interaction" key in frida\'s config is missing'

            config_type: str = interaction.get("type", False)
            assert config_type, '"type" key in frida\'s config is missing'

            return config_type == "script"

    def is_split_apk(self) -> bool:
        return self.input.is_dir()
