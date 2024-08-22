from typing import override
from fgi.loaders.base import BaseLoader
from fgi.logger import Logger
import shutil
from fgi.cmd import run_command_and_check


class SplitAPKLoader(BaseLoader):
    """Loader for Split APK files"""

    def _filter_split_apks(self) -> list[str]:
        files = [path.name for path in self.source.glob("*") if path.is_file()]
        return list(
            filter(
                lambda x: (x.startswith("base") or x.startswith("split_")) and x.endswith(".apk"),
                files,
            )
        )

    def _merge(self):
        path = self.merge_temp_path
        path.mkdir()

        candidates = self._filter_split_apks()
        Logger.debug(f"Filtered split APKs: {', '.join(candidates)} -> {path}")
        for apk in candidates:
            shutil.copy(self.source / apk, path / apk)

        Logger.info("Merging split APKs...")
        _ = run_command_and_check(
            [
                "java",
                "-jar",
                self.apkeditor_path,
                "m",
                "-i",
                path,
                "-o",
                self.output_path,
            ]
        )
        shutil.rmtree(path)

    @property
    def merge_temp_path(self):
        return self.temp_path / (self.source.absolute().name + "-merge-temp")

    @override
    def load(self):
        self._merge()

    @property
    @override
    def output_path(self):
        return self.source / (self.source.absolute().name + "-merged")

    def __del__(self):
        self.output_path.unlink(True)
        if self.merge_temp_path.exists():
            shutil.rmtree(self.merge_temp_path)
