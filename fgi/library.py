from pathlib import Path
from shutil import copy

from fgi.constants import ARCHITECTURES
from fgi.logger import Logger


class Library:
    def __init__(
        self,
        library_name: str,
        architectures: list[str],
        cache_home_path: Path,
        temp_path: Path,
    ):
        self.library_name = library_name
        self.architectures = architectures
        self.cache_home_path = cache_home_path
        self.temp_path = temp_path

    def ensure(self):
        path = self.get_root_path()
        if not path.exists():
            Logger.debug("lib/ directory does NOT exist, creating")
            path.mkdir()

    def ensure_arch(self, arch: str):
        path = self.get_arch_path(arch)
        if not path.exists():
            Logger.debug(f"lib/{arch}/ directory does NOT exist, creating")
            path.mkdir()

    def get_root_path(self) -> Path:
        return self.temp_path / "root" / "lib"

    def get_arch_path(self, arch: str) -> Path:
        return self.get_root_path() / ARCHITECTURES[arch]

    def copy_frida(self):
        self.ensure()
        for arch in self.architectures:
            self.ensure_arch(arch)
            Logger.info(f"Copying {arch} frida-gadget")
            if (self.get_arch_path(arch) / self.library_name).exists():
                raise RuntimeError("frida-gadget already injected with specified name")
            copy(
                self.cache_home_path / (arch + ".so"),
                self.get_arch_path(arch) / self.library_name,
            )

    def copy_config(self, config: str):
        for arch in self.architectures:
            Logger.debug(f"Copying {arch} config")
            with open(
                self.get_arch_path(arch)
                / self.library_name.replace(".so", ".config.so"),
                "w+",
                encoding="utf8",
            ) as f:
                f.write(config)

    def copy_script(self, script_name: str, script: bytes):
        for arch in self.architectures:
            Logger.debug(f"Copying {script_name} / {arch}")
            with open(self.get_arch_path(arch) / script_name, "wb+") as f:
                f.write(script)
