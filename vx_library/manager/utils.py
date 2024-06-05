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
            time.sleep(2)

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
    def folder_list(path):
        return [
            name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))
        ]

    folders = folder_list(f"{directory}/config/root")

    if len(folders) != 1:
        return None

    return folders[0]


def feature_has_front_base(feature_name: str) -> bool:
    return os.path.exists(f"/var/opt/vx-front-main/src/{feature_name}")


def dev_feature_has_front_base(directory: str, dev_feature_name: str) -> bool:
    return os.path.exists(f"{directory}/package.json") and os.path.exists(
        f"{directory}/src/{dev_feature_name}"
    )


# def get_dev_feature_name(directory: str) -> str | None:
#     package = read_json(f"{directory}/package.json")
#     if not package:
#         Logger.log(f"Unable to found 'package.json' file in '{directory}'", "ERROR")
#         return

#     feature_name: str = package.get("name")
#     if not feature_name:
#         Logger.log("Unable to found 'name' property in 'package.json' file", "ERROR")
#         return

#     return feature_name.replace("vx-feature-", "")


class DevFeature:
    from .requests import ShellRequests as request

    def __init__(self, directory: str):
        self.directory = directory
        self.name: str | None = None

    @property
    def has_front_package(self) -> bool:
        return os.path.exists(f"{self.directory}/package.json")

    def load(self) -> bool:
        self.name = self.request.load_feature(self.directory)

        if self.name:
            return bool(self.request.start_feature(self.name))

        return False

    def unload(self) -> bool:
        if self.name and self.request.ping():
            return bool(self.request.unload_feature(self.name))

        return False

    def reload(self) -> bool:
        return self.unload() and self.load()
