### frida-gadget injector (fgi)
Another frida-gadget injector for APK:

* Windows & Linux support
* Automatically downloads and updates dependencies
* Injects multiple frida-gadget architectures, if needed
* Built-in configs that save a lot of (copy/paste) time
* Can rename frida-gadget and script libraries to bypass detection by name
* Uses APKEditor instead of apktool to reduce the number of dependencies and amount of run time

### Installing

#### Windows (tested on Windows 11)

* Ensure Android Studio or Android Build tools installed
* Ensure JDK installed
* Ensure deps in path, if not:
  * Open start menu and type `environment`
  * Click on **Edit the system environment variables**
  * Click **Environment variables...**
  * Select `Path` and click **Edit...**
  * Add build tools and `keytool` into path:
    * Click on **New**
    * Enter path to build tools, e.g. `C:\Users\User\AppData\Local\build-tools\x.y.z`
    * Click **New** again
    * Enter path of JAVA_HOME + `bin`, e.g. `C:\Program Files\Java\jdk-22\bin`
* Run `pip install git+https://github.com/commonuserlol/fgi`
* Restart current cmd/powershell/terminal session

#### Linux

* Ensure JDK installed
* Ensure `zipalign` and `apksigner` or Android SDK installed, if not:
  * Add `~/Android/Sdk/build-tools/x.y.z` to path if you're using Android SDK
* Run `pip install git+https://github.com/commonuserlol/fgi`
  * Add `--break-system-packages` if pip refuses to install
* Add `~/.local/bin` to path

### Usage

**NOTE**: On linux if you're using `/tmp` for temp files and working with large APK, remount tmpfs using `mount -o remount,size=4G /tmp`

Run `fgi -h` to get options

#### Built-in configs

These configs are taken from [Frida website](https://frida.re)

If you need to use other configuration options, such as using v8 runtime, consider using the `--config-path` option

#### Examples

1. `fgi -i target.apk` - inject frida-gadget for **existing architectures** into target.apk with **listen** mode
   * To specify only some architectures use `-a` flag

2. `fgi -i target.apk -o out.apk` - same as 1 + ready APK will be named `out.apk` instead of `target.patched.apk`

3. `fgi -i target.apk --frida-version 16.7.19` - use specific version (16.7.19) of frida-gadget instead of the latest one

4. `fgi -i target.apk -a arm64 --offline-mode` - inject **ONLY arm64** frida-gadget into target.apk with **listen** mode and **skip frida-gadget & APKEditor update check**

5. `fgi -i . -t script -l index.js -a arm64 arm` - inject **ONLY arm64 and arm** frida-gadget into split APKs in currect directory with `index.js` as **script**

6. `fgi -i . -c myconfig.json -r .` - inject frida-gadget for **existing architectures** into **split APKs** in currect directory with **myconfig.json** config and current directory as parent temporary directory **(DANGEROUS, current directory will be filled with temp files)**
    * `fgi` **will check does config require script and raise exception** if no `-l` option provided
    * Parent temporary directory **also will be checked**

7. `fgi -i target.apk -t script -n libnotafrida.so -s libnotascript.so` - same as 1, but use **script** type + rename frida-gadget into `libnotafrida.so` and script into `libnotascript.so`
    * Both frida-gadget and script libraries name **must be prefixed** with `lib` and end with `.so`

8. `fgi -i target.apk --config-type listen --no-cleanup -v` - same as 1 + do **NOT** remove temporary directory and enable debug logs
    * Temporary directory can be found using log message:

    ```
    Decoding APK to /tmp/whatever...
                    ~~~~~~~~~~~~~
                        Here
    ```

### Acknowledgements

[objection](https://github.com/sensepost/objection) - smali injector & manifest stuff

### License

This repository is licensed under a GNU General Public v3 License.

See [LICENSE](LICENSE) file for details
