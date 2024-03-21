import os
from typing import TypedDict, List, Callable
from ..utils import exec
from ..log import Logger


class Requirement(TypedDict):
    purpose: str
    callback: Callable[[], bool]
    failure_message: str


class SetupTask:
    def __init__(
        self,
        purpose: str,
        command: str,
        undo_command: str = None,
        requirements: List[Requirement] = None,
        spinner: bool = True,
    ):
        self.is_done = False
        self.purpose = purpose
        self.command = command
        self.undo_command = undo_command
        self.requirements = requirements
        self.log_spinner = Logger.Spinner() if spinner else None

    def set_spinner(self, is_running: bool):
        if self.log_spinner:
            if is_running:
                self.log_spinner.run()
            else:
                self.log_spinner.stop()

    def check_requirements(self) -> bool:
        if self.requirements:
            Logger.log("INFO", self.purpose, "CHECKS")

            for requirement in self.requirements:
                if not requirement["callback"]():
                    Logger.log("ERROR", requirement["failure_message"])
                    return False

                Logger.log("INFO", requirement["purpose"], "OK")

        return True

    def exec(self) -> bool:
        Logger.log(
            "INFO",
            self.purpose + " ...",
        )

        if not self.check_requirements():
            Logger.log("WARNING", self.purpose, "FAILED")
            return False

        self.set_spinner(True)

        result = True
        status = "IS DONE"
        level = "WARNING"

        if not self.is_done:
            result = exec(self.command)
            status = "DONE" if result else "FAILED"
            level = "INFO" if result else "ERROR"

        self.set_spinner(False)

        Logger.log(level, self.purpose, status)
        self.is_done = result

        return result

    def undo(self) -> bool:
        if not self.undo_command:
            Logger.log("WARNING", self.purpose, "NO UNDO COMMAND")
            return False

        result = True
        status = "NOT DONE"
        level = "WARNING"

        if self.is_done:
            result = exec(self.undo_command)
            status = "UNDO" if result else "UNDO FAILED"
            level = "INFO" if result else "ERROR"

        Logger.log(level, self.purpose, status)
        self.is_done = not result
        return result


class Setup:
    def __init__(self, purpose: str, tasks: List[SetupTask]):
        self.purpose = purpose
        self.tasks = tasks

    def run(self):
        Logger.log("INFO", self.purpose)

        def undo():
            for task in reversed(self.tasks):
                if task.is_done:
                    task.undo()

            Logger.log("WARNING", self.purpose, "FAILED")
            return False

        for task in self.tasks:
            if not task.exec():
                return undo()

        Logger.log("INFO", self.purpose, "DONE")
        return True


class Commands:
    class Checkers:
        @staticmethod
        def folder_exists(path: str):
            return lambda: os.path.isdir(path)

        @staticmethod
        def folder_not_exists(path: str):
            return lambda: not os.path.isdir(path)

    @staticmethod
    def create_env(path: str) -> str:
        return f"python -m venv {path}"

    @staticmethod
    def remove_folder(path: str) -> str:
        return f"rm -r {path}"

    @staticmethod
    def install_dependencies(env_path: str, path: str):
        return f"source {env_path}/bin/activate && pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r {path}/requirements.txt"

    @staticmethod
    def install_package(env_path: str, package_path: str) -> str:
        return f"source {env_path}/bin/activate && pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir {package_path}"

    @staticmethod
    def remove_package(env_path: str, package_name: str) -> str:
        return f"source {env_path}/bin/activate && pip install --no-cache-dir --upgrade pip && pip uninstall --no-cache-dir {package_name}"

    @staticmethod
    def remove_build_folder(path: str) -> str:
        return f"rm -r {path}/build && rm -r {path}/vx_library.egg-info"

    @staticmethod
    def copy_file(file_path: str, destination: str, force: bool = False):
        return f"cp {'-f' if force else ''} {file_path} {destination}"

    @staticmethod
    def remove_file(file_path: str):
        return f"rm {file_path}"

    @staticmethod
    def path_executable_env(env_path: str, file_path: str):
        return f'sed -i "1s|.*|#!{env_path}/bin/python3|" {file_path}'
