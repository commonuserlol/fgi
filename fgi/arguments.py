import argparse
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from zipfile import ZipFile

from fgi.constants import ARCHITECTURES
from fgi.loaders.apk import APKLoader
from fgi.loaders.base import BaseLoader
from fgi.loaders.split import SplitAPKLoader


@dataclass
class Arguments:
    input: Path
    out: Path | None
    architectures: list[str]
    config_type: str | None
    config_path: Path | None
    script_path: Path | None
    library_name: str
    script_name: str
    temp_root_path: Path
    no_cleanup: bool
    offline_mode: bool
    verbose: bool

    @staticmethod
    def create():
        parser = argparse.ArgumentParser()
        _ = parser.add_argument("-i", "--input", type=Path, required=True, help="Target APK file")
        _ = parser.add_argument("-o", "--out", type=Path, help="Output APK file")  # XXX: default value determined after arguments parsed
        _ = parser.add_argument(
            "-a",
            "--architectures",
            nargs="*",
            choices=ARCHITECTURES.keys(),
            default=ARCHITECTURES.keys(),
            help="Target architecture(s) for frida-gadget",
        )

        _ = parser.add_argument(
            "-t",
            "--config-type",
            type=str,
            choices=["listen", "connect", "script"],
            help="Target config type",
        )
        _ = parser.add_argument("-c", "--config-path", type=Path, help="Custom config path")
        _ = parser.add_argument("-l", "--script-path", type=Path, help="Script path")

        _ = parser.add_argument(
            "-n",
            "--library-name",
            type=str,
            default="libfrida.so",
            help='frida-gadget library name, must have "lib" at start and "so" at end',
        )
        _ = parser.add_argument(
            "-s",
            "--script-name",
            type=str,
            default="libscript.so",
            help='frida-gadget script name, must have "lib" at start and "so" at end',
        )

        _ = parser.add_argument(
            "-r",
            "--temp-root-path",
            type=Path,
            default=tempfile.gettempdir(),
            help="Root path where temporary directory will be created",
        )

        _ = parser.add_argument(
            "--no-cleanup",
            action="store_true",
            help="Do not remove temporary directory (useful for debugging)",
        )
        _ = parser.add_argument("--offline-mode", action="store_true", help="Disable updates check for deps")
        _ = parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Verbose logging (useful for debugging)",
        )

        args = parser.parse_args()
        return Arguments(
            args.input,  # pyright: ignore[reportAny]
            args.out,  # pyright: ignore[reportAny]
            args.architectures,  # pyright: ignore[reportAny]
            args.config_type,  # pyright: ignore[reportAny]
            args.config_path,  # pyright: ignore[reportAny]
            args.script_path,  # pyright: ignore[reportAny]
            args.library_name,  # pyright: ignore[reportAny]
            args.script_name,  # pyright: ignore[reportAny]
            args.temp_root_path,  # pyright: ignore[reportAny]
            args.no_cleanup,  # pyright: ignore[reportAny]
            args.offline_mode,  # pyright: ignore[reportAny]
            args.verbose,  # pyright: ignore[reportAny]
        )

    def validate(self):
        if not self.is_split_apk():  # XXX: Assume that split APKs always exists
            assert self.input.exists(), "Input APK doesn't exist"
        if self.out is None:
            if ".apk" not in self.input.name:
                self.out = Path.cwd() / (self.input.absolute().name + ".patched.apk")
            else:
                self.out = Path.cwd() / self.input.name.replace(".apk", ".patched.apk")
        assert not self.out.exists(), 'Out path is exist, delete, rename or specify manually via "-o"'
        assert self.out.name.endswith(".apk"), "Out filename must endswith .apk"
        assert self.is_builtin_config() or (self.config_path and not self.config_type), 'Specify "config-type" or "config-path"'
        if self.is_script_required():
            assert self.script_path, 'Script is required when "config-type" equals "script" or config provided via "config-path" have "type": "script"'
            assert self.script_path.exists(), "Script doesn't exist"
        assert self.library_name.startswith("lib") and self.library_name.endswith(".so"), "Invalid name for frida library"
        assert self.script_name.startswith("lib") and self.script_name.endswith(".so"), "Invalid name for frida script"
        assert self.temp_root_path.exists(), "Root temp path doesn't exist"

    def is_builtin_config(self) -> bool:
        return self.config_path is None and self.config_type is not None

    def is_script_required(self) -> bool:
        if self.config_type == "script":
            return True
        if self.config_path:
            with open(self.config_path, "r", encoding="utf8") as f:
                config_dict: dict[str, dict[str, Any]] = json.load(f)
            interaction = config_dict.get("interaction", None)
            assert interaction, '"interaction" key in frida\'s config is missing'

            config_type: str = interaction.get("type", None)
            assert config_type, '"type" key in frida\'s config is missing'

            return config_type == "script"
        return False

    def is_split_apk(self):
        return self.input.is_dir()

    def is_xapk(self):
        return self.input.suffix == ".xapk"

    def is_contain_obb(self):
        with ZipFile(self.input) as zipfile:
            return self.is_xapk() and any(filter(lambda x: x.filename.startswith("Android"), zipfile.filelist))  # pyright: ignore[reportUnknownMemberType, reportUnknownLambdaType, reportAttributeAccessIssue]

    def pick_loader(self) -> type[BaseLoader]:
        if self.is_split_apk():
            return SplitAPKLoader
        elif self.is_split_apk():
            raise RuntimeError("XAPK is not supported yet")
        else:
            return APKLoader
