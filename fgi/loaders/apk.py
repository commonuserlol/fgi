from typing import override

from fgi.loaders.base import BaseLoader


class APKLoader(BaseLoader):
    """Stub loader for APK files"""

    @override
    def load(self):
        pass

    @property
    @override
    def output_path(self):
        return self.source
