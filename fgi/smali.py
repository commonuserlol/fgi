from pathlib import Path

from fgi.constants import SMALI_FULL_LOAD_LIBRARY, SMALI_PARTIAL_LOAD_LIBRARY
from fgi.logger import Logger


class Smali:
    def __init__(self, path: Path):
        self.path = path
        with open(self.path, "r", encoding="utf8") as f:
            self.content = f.readlines()

    @staticmethod
    def find(temp_path: Path, entrypoint: str):
        target_smali = entrypoint.split(".")[-1] + ".smali"

        Logger.info(f"Looking for {target_smali}...")

        for child in (temp_path / "smali").rglob("*"):
            if target_smali == child.name.split("/")[-1]:
                Logger.info(f"Found at {child}")

                return Smali(child)
        raise RuntimeError(f"Couldn't find smali containing entrypoint ({entrypoint})")

    def find_inject_point(self, start: int) -> int:
        pos = start
        in_annotation = False
        while pos + 1 < len(self.content):
            pos = pos + 1
            line = self.content[pos].strip()

            # skip empty lines
            if not line:
                continue

            # skip locals
            if line.startswith(".locals "):
                continue

            # skip annotations
            if in_annotation or line.startswith(".annotation "):
                in_annotation = True
                continue

            if line.startswith(".end annotation"):
                in_annotation = False
                continue

            return pos - 1
        raise RuntimeError("Failed to determine injection point")

    def find_end_of_method(self, start: int) -> int:
        end_methods = [(i + start) for i, x in enumerate(self.content[start:]) if ".end method" in x]

        if len(end_methods) <= 0:
            raise RuntimeError("Coundn't find the end of the existing constructor")

        end_of_method = end_methods[0] - 1

        # check if the constructor has a return type call. if it does,
        # move up one line again to inject our loadLibrary before the return
        if "return" in self.content[end_of_method]:
            end_of_method -= 1

        return end_of_method

    def put_load_library(self, library_name: str, marker: int):
        if "init" in self.content[marker]:
            Logger.debug("<init> is present in entry activity")

            inject_point = self.find_inject_point(marker)

            self.content = self.content[:inject_point] + (SMALI_PARTIAL_LOAD_LIBRARY % library_name).splitlines(keepends=True) + self.content[inject_point:]

        else:
            Logger.debug("<init> is NOT present in entry activity")

            self.content = self.content[:marker] + (SMALI_FULL_LOAD_LIBRARY % library_name).splitlines(keepends=True) + self.content[marker:]

    def update_locals(self, marker: int):
        end_of_method = self.find_end_of_method(marker)

        defined_locals = [i for i, x in enumerate(self.content[marker:end_of_method]) if ".locals" in x]

        if len(defined_locals) <= 0:
            Logger.warn("Couldn't to determine any .locals for the target constructor")

        # determine the offset for the first matched .locals definition
        locals_smali_offset = defined_locals[0] + marker

        try:
            defined_local_value = self.content[locals_smali_offset].split(" ")[-1]
            defined_local_value_as_int = int(defined_local_value, 10)
            new_locals_value = defined_local_value_as_int + 1

        except ValueError:
            Logger.warn("Couldn't to parse .locals value for the injected constructor")
            return

        self.content[locals_smali_offset] = self.content[locals_smali_offset].replace(str(defined_local_value_as_int), str(new_locals_value))

    def perform_injection(self, library_name: str):
        library_name = library_name.replace("lib", "").replace(".so", "")
        Logger.info(f'Injecting loadLibrary("{library_name}")')

        marker = [i for i, x in enumerate(self.content) if "# direct methods" in x]

        # ensure we got a marker
        if len(marker) <= 0:
            raise RuntimeError("Couldn't to determine position to inject a loadLibrary call")

        # pick the first position for the inject. add one line as we
        # want to inject right below the comment we matched
        marker_value = marker[0] + 1

        self.put_load_library(library_name, marker_value)
        self.update_locals(marker_value)

    def __del__(self):
        with open(self.path, "w", encoding="utf8") as f:
            f.writelines(self.content)
