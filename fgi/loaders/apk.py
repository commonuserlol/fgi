from fgi.loaders.base import BaseLoader


class APKLoader(BaseLoader):
    """Stub loader for APK files"""
    def load(self):
        pass

    @property
    def output_path(self):
        return self.source
