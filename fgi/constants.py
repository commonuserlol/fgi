ARCHITECTURES = {
    "arm": "armeabi-v7a",
    "arm64": "arm64-v8a",
    "x86": "x86",
    "x86_64": "x86_64",
}
TEMP_PATH_LEN = 12
FRIDA_URL = "https://api.github.com/repos/frida/frida/releases/latest"
FRIDA_TAGGED_URL = "https://api.github.com/repos/frida/frida/releases/tags/%s"
FRIDA_GADGET_ARCH_PATTERN = r"android-(\w+[-\w]*).so"
APKEDITOR_URL = "https://api.github.com/repos/REAndroid/APKEditor/releases/latest"
APKEDITOR_TAGGED_URL = "https://api.github.com/repos/REAndroid/APKEditor/releases/tags/%s"

SMALI_FULL_LOAD_LIBRARY = (
    ".method static constructor <init>()V\n"  # Using <clinit> may cause method overflow
    "   .locals 0\n"
    "\n"
    "   .prologue\n"
    '   const-string v0, "%s"\n'
    "\n"
    "   invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V\n"
    "\n"
    "   return-void\n"
    ".end method\n"
)

SMALI_PARTIAL_LOAD_LIBRARY = '\n    const-string v0, "%s"\n' + "\n" + "    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V\n"

PREFIXES = ["m", "b", "z", "s"]
