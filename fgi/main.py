import logging
import traceback

from fgi.apk import APK
from fgi.arguments import Arguments
from fgi.cache import Cache
from fgi.frida_config import CONFIG_TYPES
from fgi.library import Library
from fgi.logger import Logger
from fgi.manifest import Manifest
from fgi.smali import Smali


class App:
    def run(self):
        arguments = Arguments.create()

        Logger.initialize(arguments.verbose)

        arguments.validate()

        cache = Cache()
        cache.ensure()

        if not arguments.offline_mode:
            cache.check_and_download_frida()
            cache.check_and_download_apkeditor()
        else:
            Logger.warn("Skipping update check for deps")

        apk = APK(arguments, cache.get_apkeditor_path())
        if arguments.is_split_apk():
            apk.merge()
        apk.decode()

        entrypoint = apk.get_entry_activity()
        smali = Smali.find(apk.get_temp_path(), entrypoint)
        smali.perform_injection(arguments.library_name)
        del smali

        library = Library(
            arguments.library_name,
            arguments.architectures,
            cache.get_home_path(),
            apk.get_temp_path(),
        )
        library.copy_frida()

        if arguments.is_builtin_config():
            library.copy_config(
                CONFIG_TYPES[arguments.config_type] % arguments.script_name
                if arguments.is_script_required()
                else CONFIG_TYPES[arguments.config_type]
            )
        else:
            with open(arguments.script_path, "r", encoding="utf8") as f:
                config = f.read()
                library.copy_config(config)

        if arguments.is_script_required():
            with open(arguments.script_path, "rb") as f:
                script = f.read()
                library.copy_script(arguments.script_name, script)
        del library

        manifest = Manifest(apk.get_temp_path() / "AndroidManifest.xml")
        manifest.enable_extract_native_libs()
        del manifest

        apk.build()
        apk.zipalign()
        if not cache.get_key_path().exists():
            apk.generate_debug_key(cache.get_key_path())
        apk.sign(cache.get_key_path())
        del apk
        del cache

        Logger.info(f"APK is ready at {arguments.out}")


def main():
    app = App()
    try:
        app.run()
    except KeyboardInterrupt:
        Logger.warn("Aborting...")
    except (RuntimeError, AssertionError) as e:
        Logger.error(e)
    except Exception as e:
        Logger.error(f"Unexpected exception: {e}")
        Logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()
