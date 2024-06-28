import json
import re
from pathlib import Path

from fgi.logger import Logger
from fgi.constants import (
    FRIDA_GADGET_ARCH_PATTERN,
    FRIDA_TAGGED_URL,
    FRIDA_URL,
    APKEDITOR_TAGGED_URL,
    APKEDITOR_URL,
    ARCHITECTURES,
)
from fgi.downloader import Downloader


class Cache:
    def __init__(self):
        self.home = Path.home() / ".fgi"
        self.metadata = self.home / "metadata.json"
        self.is_metadata_open = False
        self.metadata_dict: dict[str, str] = None

    def _open_metadata(self):
        if self.is_metadata_open:
            return
        with open(self.metadata, "r+", encoding="utf8") as f:
            self.metadata_dict = json.load(f)
        self.is_metadata_open = True

    def _close_metadata(self):
        if not self.is_metadata_open:
            return
        with open(self.metadata, "w+", encoding="utf8") as f:
            json.dump(self.metadata_dict, f)
        self.is_metadata_open = False

    def ensure(self):
        if not self.home.exists():
            self.home.mkdir()
        if not self.metadata.exists():
            with open(self.metadata, "w+", encoding="utf8") as f:
                json.dump({"frida": "v0", "apkeditor": "v0"}, f)

    def check_and_download_frida(self):
        downloader = Downloader(FRIDA_URL, FRIDA_TAGGED_URL)
        tag = downloader.get_latest_release_tag()
        if tag == self.get_version("frida"):
            return

        Logger.info("Downloading frida-gadget...")

        assets = downloader.get_assets()
        for asset in assets:
            if not ("gadget" in asset and "android" in asset):
                continue
            arch = re.search(FRIDA_GADGET_ARCH_PATTERN, asset).group(1)
            if arch in ARCHITECTURES.keys():
                Logger.info(f"Downloading {arch} frida-gadget...")

                data = downloader.get_asset(asset)
                decompressed_data = downloader.decompress(data)

                with open(self.home / f"{arch}.so", "wb+") as f:
                    f.write(decompressed_data)
        self.set_version("frida", tag)

    def check_and_download_apkeditor(self):
        downloader = Downloader(APKEDITOR_URL, APKEDITOR_TAGGED_URL)
        tag = downloader.get_latest_release_tag()
        if tag == self.get_version("apkeditor"):
            return

        Logger.info("Downloading APKEditor...")

        assets: list[str] = downloader.get_assets()
        assert len(assets) == 1, "Wrong asset count for APKEditor"
        data = downloader.get_asset(assets[0])

        with open(self.get_apkeditor_path(), "wb+") as f:
            f.write(data)
        self.set_version("apkeditor", tag)

    def get_version(self, key: str) -> str:
        self._open_metadata()
        return self.metadata_dict.get(key)

    def set_version(self, key: str, value: str):
        self._open_metadata()
        self.metadata_dict[key] = value

    def get_home_path(self) -> Path:
        return self.home

    def get_apkeditor_path(self) -> Path:
        return self.home / "apkeditor.jar"

    def get_key_path(self) -> Path:
        return self.home / "debug.keystore"

    def __del__(self):
        self._close_metadata()
