import sys, signal
from .utils import use_sudo, DevFeature, get_current_tty
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
    def log_to_tty():
        from .requests import ShellRequests

        if ShellRequests.ping():
            from time import sleep
            from signal import signal, SIGINT

            print("Listening to logs from Vixen Shell ([ctrl + C] to exit) ...\n")

            def on_keyboard_interrupt(signum, frame):
                if ShellRequests.ping():
                    ShellRequests.unlog_to_tty(get_current_tty())

                print("\nStop listening to logs from Vixen Shell")
                exit(0)

            signal(SIGINT, on_keyboard_interrupt)

            ShellRequests.log_to_tty(get_current_tty())

            while True:
                sleep(1)
        else:
            Logger.log("Vixen Shell is not running", "WARNING")

    @staticmethod
    @use_sudo(False)
    def dev(directory: str):
        from .utils import get_vite_process

        feature = DevFeature(directory)
        vite_process = None

        if feature.has_front_package:
            vite_process = get_vite_process(directory)
            if not vite_process:
                return

        def exit_dev_mode():
            exit_code = 0

            if feature.unload():
                Logger.log(f"Unload feature '{feature.name}'", suffix="SUCCESS")
            else:
                Logger.log("Unload feature", "ERROR", "FAILED")
                exit_code = 1

            Logger.log("Exit Vixen Shell Dev Mode ...")
            sys.exit(exit_code)

        if vite_process:
            if feature.load():
                Logger.log(f"Load feature '{feature.name}'", suffix="SUCCESS")

                vite_process.start()
                feature.start()

                vite_process.join()
                exit_dev_mode()
            else:
                Logger.log("Load feature", "ERROR", suffix="FAILED")

        if not vite_process:

            def signal_handler(sig, frame):
                exit_dev_mode()

            signal.signal(signal.SIGINT, signal_handler)

            if feature.load():
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

                        Logger.log(f"Reload feature '{feature.name}'", suffix="SUCCESS")
                        feature.start()

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
    def start_feature(feature_name: str):
        from .requests import ShellRequests

        result = ShellRequests.start_feature(feature_name)
        if result != None:
            print(f"Start '{result}' feature")

    @staticmethod
    @use_sudo(False)
    def stop_feature(feature_name: str):
        from .requests import ShellRequests

        result = ShellRequests.stop_feature(feature_name)
        if result != None:
            print(f"Stop '{result}' feature")

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

    @staticmethod
    @use_sudo(False)
    def feature_task_names(feature_name: str):
        from .requests import ShellRequests

        result = ShellRequests.feature_task_names(feature_name)
        if result != None:
            print(result)

    @staticmethod
    @use_sudo(False)
    def run_feature_task(feature_name: str, task_name: str, args: list | None):
        from .requests import ShellRequests

        result = ShellRequests.run_feature_task(
            feature_name, task_name, args if args else []
        )
        if result != None:
            print(f"Run task '{task_name}' from feature '{feature_name}'")
            print(f"Return: {result}")
