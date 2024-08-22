from abc import ABC, abstractmethod
from pathlib import Path


class BaseLoader(ABC):
    def __init__(self, apkeditor_path: Path, source: Path, temp_path: Path):
        self.apkeditor_path = apkeditor_path
        self.source = source
        self.temp_path = temp_path

    @abstractmethod
    def load(self):
        pass

    @property
    @abstractmethod
    def output_path(self) -> Path:
        pass
