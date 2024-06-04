import os, sys, signal
from .utils import use_sudo, DevFeature
from .logger import Logger
from ..cli import Cli


class ShellManager:
    @staticmethod
    @use_sudo(False)
    def open():
        from .requests import ShellRequests

        ShellRequests.open()

    @staticmethod
    @use_sudo(False)
    def close():
        from .requests import ShellRequests

        ShellRequests.close()

    @staticmethod
    @use_sudo(False)
    def dev(directory: str):
        from .requests import ShellRequests
        from .utils import get_vite_process

        if os.path.exists(f"{directory}/package.json"):

            def load_feature() -> str:
                return ShellRequests.load_feature(directory)

            feature_name = load_feature()
            if not feature_name:
                return

            vite_process = get_vite_process(directory)
            if not vite_process:
                ShellRequests.unload_feature(feature_name)
                return

            vite_process.start()

            if ShellRequests.start_feature(feature_name):
                print(f"  \033[92m➜\033[0m  Vixen: start feature '{feature_name}'")
                vite_process.join()
            else:
                print(
                    f"  \033[31m➜\033[0m  Vixen: Error on starting feature '{feature_name}'"
                )
                vite_process.terminate()

            if ShellRequests.ping():
                ShellRequests.unload_feature(feature_name)

        else:
            feature = DevFeature(directory)

            def signal_handler(sig, frame):
                Logger.log("Exit Vixen Shell Dev Mode ...")
                if feature.unload():
                    Logger.log(f"Unload feature '{feature.name}'", suffix="SUCCESS")
                    sys.exit(0)

                Logger.log(f"Unload feature '{feature.name}'", "ERROR", "FAILURE")
                sys.exit(1)

            signal.signal(signal.SIGINT, signal_handler)

            if feature.load():
                os.system("clear")
                Logger.log(f"Load feature '{feature.name}'", suffix="SUCCESS")

                while True:
                    Logger.log(
                        "type (r and ENTER) to reload feature or (Ctrl + C) to exit"
                    )

                    choice = Cli.Input.get_answer(
                        [Cli.Input.Filter(type="include", values=["r"])],
                        "",
                    )

                    if choice == "r":
                        if not feature.reload():
                            Logger.log(
                                f"Reload feature '{feature.name}'", "ERROR", "FAILURE"
                            )
                            break

                        os.system("clear")
                        Logger.log(f"Reload feature '{feature.name}'", suffix="SUCCESS")

    @staticmethod
    @use_sudo(False)
    def feature_names():
        from .requests import ShellRequests

        print(ShellRequests.feature_names())
