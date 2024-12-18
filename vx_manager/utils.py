import os, sys, time, subprocess, multiprocessing, json, re, packaging
from vx_path import VxPath
from .logger import Logger


def read_json(file_path: str) -> dict | None:
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)


def write_json(file_path: str, data: dict):
    if os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    else:
        with open(file_path, "x", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)


def get_vx_package_version(library_path: str) -> str | None:
    with open(f"{library_path}/setup.py", "r") as f:
        content = f.read()

    match = re.search(r'version\s*=\s*["\'](.*?)["\']', content)

    if match:
        return match.group(1)


def is_sup_version(current_version, new_version):
    current = packaging.version.parse(current_version)
    new = packaging.version.parse(new_version)

    if current >= new:
        return False

    return True


def get_root_feature_names():
    feature_names: list[str] = []

    for item in os.listdir(VxPath.ROOT_FEATURE_MODULES):
        path = f"{VxPath.ROOT_FEATURE_MODULES}/{item}"

        if os.path.isdir(path):
            feature_names.append(item)

    return feature_names


def get_dev_feature_name(directory: str) -> str | None:
    def folder_list(path):
        return [
            name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))
        ]

    folders = folder_list(f"{directory}/root")

    if len(folders) != 1:
        return None

    return folders[0]


def get_vite_process(directory: str):
    def vite_process():
        sub_process = subprocess.Popen(
            f"{directory}/node_modules/.bin/vite {directory}", shell=True
        )

        sub_process.wait()

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
                self.terminate()

        def terminate(self):
            self.process.terminate()
            self.process.join()

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


def get_current_tty():
    try:
        return os.ttyname(sys.stdout.fileno())
    except Exception as e:
        raise RuntimeError("Unable to retrieve current terminal") from e


class DevFeature:
    from .requests import ShellRequests as request

    def __init__(self, directory: str):
        self.directory = directory
        self.name: str | None = None

    @property
    def has_front_package(self) -> bool:
        return os.path.exists(f"{self.directory}/package.json")

    def load(self) -> bool:
        self.name = self.request.load_feature(self.directory, get_current_tty())
        return bool(self.name)

    def start(self) -> bool:
        return bool(self.request.start_feature(self.name))

    def unload(self) -> bool:
        if self.name and self.request.ping():
            return bool(self.request.unload_feature(self.name))

        return False

    def reload(self) -> bool:
        return self.unload() and self.load()
