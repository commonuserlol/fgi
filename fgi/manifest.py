from pathlib import Path
from xml.etree import ElementTree
from fgi.logger import Logger


class Manifest:
    def __init__(self, xml_path: Path):
        ElementTree.register_namespace(
            "android", "http://schemas.android.com/apk/res/android"
        )
        self.path = xml_path
        with open(self.path, "r", encoding="utf8") as f:
            self.content = ElementTree.parse(f)

    def enable_extract_native_libs(self):
        root = self.content.getroot()
        application_tag = root.findall("application")[0]
        if (
            "{http://schemas.android.com/apk/res/android}extractNativeLibs"
            in application_tag.attrib
            and application_tag.attrib[
                "{http://schemas.android.com/apk/res/android}extractNativeLibs"
            ]
            == "false"
        ):
            Logger.debug("Enabling extractNativeLibs in manifest")
            application_tag.attrib[
                "{http://schemas.android.com/apk/res/android}extractNativeLibs"
            ] = "true"

    def __del__(self):
        self.content.write(self.path, encoding="utf8", xml_declaration=True)
