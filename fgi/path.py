import random
import string
from pathlib import Path

from fgi.constants import PREFIXES, TEMP_PATH_LEN
from fgi.logger import Logger


class PathUtils:
    def __init__(self, input: Path, out: Path, temp_root_path: Path):
        self.input_apk_path = input
        self.out_apk_path = out
        self.temp_path = temp_root_path / "".join(
            random.choices(string.ascii_letters, k=TEMP_PATH_LEN)
        )

    def get_input_apk_path(self) -> Path:
        return self.input_apk_path

    def get_out_apk_path(self) -> Path:
        return self.out_apk_path

    def get_temp_path(self) -> Path:
        return self.temp_path

    def _get_temp_apk_path(self, suffix: str) -> Path:
        if "." + suffix not in self.input_apk_path.name:
            child = self.input_apk_path.name.replace(".apk", f".{suffix}.apk")
        else:
            child = self.input_apk_path.name
        for p in PREFIXES:
            if p != suffix:
                child = child.replace(f".{p}.apk", ".apk")
        return self.temp_path.parent / child

    def get_merged_apk_path(self) -> Path:
        if ".apk" not in self.input_apk_path.name:
            Logger.debug("Split APKs detected, fixing temp path")
            return self.temp_path.parent / (self.input_apk_path.name + ".m.apk")
        return self._get_temp_apk_path("m")

    def get_built_apk_path(self) -> Path:
        return self._get_temp_apk_path("b")

    def get_zipaligned_apk_path(self) -> Path:
        return self._get_temp_apk_path("z")

    def get_signed_apk_path(self) -> Path:
        return self._get_temp_apk_path("s")

    def set_input_apk_path(self, value: Path) -> Path:
        self.input_apk_path = value

    def switch_input_to_merged(self):
        self.set_input_apk_path(self.get_merged_apk_path())
