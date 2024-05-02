import os, time, subprocess, multiprocessing, json
from .logger import Logger


def get_vite_process(directory: str):
    def vite_process():
        process = subprocess.Popen(
            f"{directory}/node_modules/.bin/vite {directory}", shell=True
        )
        process.wait()

    class ProcessReference:
        def __init__(self):
            self.process = multiprocessing.Process(target=vite_process)

        @property
        def is_alive(self) -> bool:
            return self.process.is_alive()

        def start(self):
            self.process.start()
            time.sleep(1)

        def join(self):
            try:
                self.process.join()
            except KeyboardInterrupt:
                self.process.terminate()

        def terminate(self):
            self.process.terminate()

    if not os.path.exists(f"{directory}/node_modules"):
        Logger.log("Node modules not found", "ERROR")
        return

    return ProcessReference()


def use_sudo(value: bool):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if bool(os.geteuid() == 0) == value:
                # @errorHandling exclude
                return func(*args, **kwargs)
            else:
                Logger.log(
                    (
                        "This command must be used with 'sudo'"
                        if value
                        else "Cannot use this command with 'sudo'"
                    ),
                    "WARNING",
                )
                return None

        return wrapper

    return decorator


def read_json(file_path: str) -> dict | None:
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)


def get_dev_feature_name(directory: str) -> str | None:
    package = read_json(f"{directory}/package.json")
    if not package:
        Logger.log(f"Unable to found 'package.json' file in '{directory}'", "ERROR")
        return

    feature_name: str = package.get("name")
    if not feature_name:
        Logger.log("Unable to found 'name' property in 'package.json' file", "ERROR")
        return

    return feature_name.replace("vx-feature-", "")
