import os, sys, signal
from .utils import use_sudo, DevFeature
from .logger import Logger
from vx_cli import Cli


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
        from .utils import get_vite_process

        feature = DevFeature(directory)
        vite_process = None

        if os.path.exists(f"{directory}/package.json"):
            vite_process = get_vite_process(directory)
            if not vite_process:
                return

        def signal_handler(sig, frame):
            Logger.log("Exit Vixen Shell Dev Mode ...")

            if vite_process and vite_process.is_alive:
                vite_process.terminate()

            if feature.unload():
                Logger.log(f"Unload feature '{feature.name}'", suffix="SUCCESS")
                sys.exit(0)

            Logger.log("Unload feature", "ERROR", "FAILED")
            sys.exit(1)

        signal.signal(signal.SIGINT, signal_handler)

        if feature.load():
            if vite_process and not vite_process.is_alive:
                vite_process.start()

            os.system("clear")
            Logger.log(f"Load feature '{feature.name}'", suffix="SUCCESS")
            feature.start()

            while True:
                Logger.log("(r and ENTER) to reload feature, (Ctrl+C) to exit")

                choice = Cli.Input.get_answer(
                    [
                        Cli.Input.Filter(
                            type="include",
                            values=["r"],
                            reason="(r and ENTER) to reload feature, (Ctrl+C) to exit",
                        )
                    ],
                    "",
                )

                if choice == "r":
                    if not feature.reload():
                        Logger.log("Reload feature", "ERROR", "FAILED")
                        break

                    os.system("clear")
                    Logger.log(f"Reload feature '{feature.name}'", suffix="SUCCESS")
                    feature.start()

            if vite_process and vite_process.is_alive:
                vite_process.terminate()

        else:
            Logger.log("Load feature", "ERROR", suffix="FAILED")

    @staticmethod
    @use_sudo(False)
    def feature_names():
        from .requests import ShellRequests

        result = ShellRequests.feature_names()
        if result != None:
            print(result)

    @staticmethod
    @use_sudo(False)
    def feature_frame_ids(feature_name: str):
        from .requests import ShellRequests

        result = ShellRequests.feature_frame_ids(feature_name)
        if result != None:
            print(result)

    @staticmethod
    @use_sudo(False)
    def toggle_feature_frame(feature_name: str, frame_id: str):
        from .requests import ShellRequests

        result = ShellRequests.toggle_feature_frame(feature_name, frame_id)
        if result != None:
            print(result)

    @staticmethod
    @use_sudo(False)
    def open_feature_frame(feature_name: str, frame_id: str):
        from .requests import ShellRequests

        result = ShellRequests.open_feature_frame(feature_name, frame_id)
        if result != None:
            print(result)

    @staticmethod
    @use_sudo(False)
    def close_feature_frame(feature_name: str, frame_id: str):
        from .requests import ShellRequests

        result = ShellRequests.close_feature_frame(feature_name, frame_id)
        if result != None:
            print(result)
