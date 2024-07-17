### frida-gadget injector (fgi)
Another frida-gadget injector into APK with some key features:

* Automatically downloads and updates dependencies
* Ability to inject multiple frida-gadget architectures at once
* Built-in configs that save a lot of time during initial testing
* Renaming frida-gadget and script libraries to bypass detection by name
* Using APKEditor instead of apktool to reduce the number of dependencies and faster build

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
      * Enter path to build tools, e.g. `C:\Users\User\AppData\Local\build-tools\35.0.0`
        * Note: version of build tools may be different
      * Click **New** again
      * Enter path of JAVA_HOME + `/bin`, e.g. `C:\Program Files\Java\jdk-22\bin`

#### Linux
* Ensure JDK installed
* Ensure `zipalign` and `apksigner` or Android SDK installed, if not:
    * Add `~/Android/Sdk/build-tools/x.y.z` to path if you're using Android SDK
* Run `pip install git+https://github.com/commonuserlol/fgi`
    * Add `--break-system-packages` if pip refuses to install
* Add `~/.local/bin` to path

### Usage
Run `fgi -h` to get options

#### Built-in configs
These configs are slightly edited from frida's [site](https://frida.re)
* `listen` and `connect` are using `0.0.0.0` instead of `127.0.0.1`
* `script` is not modified

If you need to use other configuration options, such as using v8 runtime, consider using the `--config-path` option

#### Examples
1. `fgi -i target.apk --config-type listen` - inject **arm, arm64, x86, x86_64** frida-gadget into target.apk with **listen** mode

2. `fgi -i target.apk -t listen -o out.apk` - same as 1 + ready APK will be named `out.apk` instead of `target.patched.apk`

3. `fgi -i target.apk -t listen -a arm64 --offline-mode` - inject **ONLY arm64** frida-gadget into target.apk with **listen** mode and skip frida-gadget & APKEditor update check

4. `fgi -i . -t script -l index.js -a arm` - inject **ONLY arm** frida-gadget into split APKs in currect directory with `index.js` **script**

5. `fgi -i . -c myconfig.json -r .` - inject **arm, arm64, x86, x86_64** frida-gadget into **split APKs** in currect directory with **myconfig.json** config and current directory as parent temporary directory **(DANGEROUS, current directory will be filled with temp files)**
    * `fgi` **will check does config require script and raise exception** if no `-l` option provided
    * Parent temporary directory **also will be checked**

6. `fgi -i target.apk -t listen -n libnotafrida.so -s libnotascript.so` - same as 1 + rename frida-gadget into `libnotafrida.so` and script into `libnotascript.so`
    * Both frida-gadget and script libraries name **should be prefixed** with `lib` and end with `.so`

7. `fgi -i target.apk --config-type listen --no-cleanup -v` - same as 1 + do **NOT** remove temporary directory and enable debug logs
    * Temporary directory can be found using log message:
    ```
    Decoding APK to /tmp/whatever...
                    ~~~~~~~~~~~~~
                        Here
    ```

### Acknowledgements
[objection](https://github.com/sensepost/objection) - smali injector & manifest stuff

### License
This repository is licensed under a GNU General Public v3 License.<br>
See [LICENSE](LICENSE) file for details
