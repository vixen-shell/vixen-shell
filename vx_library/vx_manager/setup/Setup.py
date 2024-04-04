import os
from typing import TypedDict, List, Callable, Optional
from .utils import exec
from ..log import Logger


class Issue(TypedDict):
    purpose: str
    command: str


class Requirement(TypedDict):
    purpose: str
    callback: Callable[[], bool]
    failure_message: str
    issue: Optional[Issue]


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
                    if not requirement.get("issue"):
                        Logger.log("ERROR", requirement["failure_message"])
                        return False
                    else:
                        Logger.log("WARNING", requirement["failure_message"])
                        issue = requirement["issue"]

                        if exec(issue["command"]):
                            Logger.log("WARNING", issue["purpose"], "ISSUE")
                        else:
                            Logger.log("ERROR", "Unable to apply issue", "ISSUE")
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
            return True

        result = True
        status = "NOT DONE"
        level = "WARNING"

        if self.is_done:
            result = exec(self.undo_command)
            status = "UNDO" if result else "UNDO FAILED"
            level = "WARNING" if result else "ERROR"

        Logger.log(level, self.purpose, status)
        self.is_done = not result
        return result


class Setup:
    def __init__(self, purpose: str, tasks: List[SetupTask]):
        self.purpose = purpose
        self.tasks = tasks

    def run(self):
        print()
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
        def folder(path: str, exists: bool):
            return (
                (lambda: os.path.isdir(path))
                if exists
                else (lambda: not os.path.isdir(path))
            )

        @staticmethod
        def folder_exists(path: str):
            return lambda: os.path.isdir(path)

        @staticmethod
        def folder_not_exists(path: str):
            return lambda: not os.path.isdir(path)

    # ---------------------------------------------- - - -
    # User
    @staticmethod
    def user(command: str):
        return f"sudo -u {os.getlogin()} {command}"

    # ---------------------------------------------- - - -
    # Environment
    @staticmethod
    def env_create(env_dir: str) -> str:
        return f"python -m venv {env_dir}"

    @staticmethod
    def env_dependencies(env_dir: str, requirements_dir: str):
        return f"source {env_dir}/bin/activate && pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r {requirements_dir}/requirements.txt"

    @staticmethod
    def env_install(env_dir: str, package_dir: str) -> str:
        return f"source {env_dir}/bin/activate && pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir {package_dir}"

    @staticmethod
    def env_remove(env_dir: str, package_name: str) -> str:
        return f"source {env_dir}/bin/activate && pip install --no-cache-dir --upgrade pip && pip uninstall --no-cache-dir {package_name}"

    @staticmethod
    def env_path_executable(env_dir: str, file: str):
        return f'sed -i "1s|.*|#!{env_dir}/bin/python3|" {file}'

    @staticmethod
    def folder_remove_build(package_dir: str) -> str:
        return f"rm -r {package_dir}/build && rm -r {package_dir}/vx_library.egg-info"

    # ---------------------------------------------- - - -
    # Folders
    @staticmethod
    def folder_create(dir: str) -> str:
        return f"mkdir -p {dir}"

    @staticmethod
    def folder_remove(dir: str) -> str:
        return f"rm -r {dir}"

    @staticmethod
    def folder_copy(source: str, destination: str, force: bool = False):
        return f"cp -r{'f' if force else ''} {source} {destination}"

    # ---------------------------------------------- - - -
    # Files
    @staticmethod
    def file_copy(source: str, destination: str, force: bool = False):
        return f"cp {'-f' if force else ''} {source} {destination}"

    @staticmethod
    def file_remove(file: str):
        return f"rm {file}"

    # ---------------------------------------------- - - -
    # Files and folder
    @staticmethod
    def rename(source: str, destination: str):
        return f"mv {source} {destination}"

    # ---------------------------------------------- - - -
    # Git
    @staticmethod
    def git_get_archive(url: str, destination: str):
        return f"curl -s -L {url} -o /tmp/vx-git-archive.zip && unzip -o /tmp/vx-git-archive.zip -d {destination} && rm /tmp/vx-git-archive.zip"

    # ---------------------------------------------- - - -
    # Yarn
    @staticmethod
    def yarn_install(package_dir: str):
        return f"cd {package_dir} && yarn install"

    @staticmethod
    def yarn_build(package_dir: str):
        return f"cd {package_dir} && yarn build"

    # ---------------------------------------------- - - -
    # JSON
    @staticmethod
    def json_patch_feature_name_property(file: str, name: str):
        old_field = '"name": "feature"'
        new_field = f'"name": "{name}"'
        return f"sed -i 's/{old_field}/{new_field}/' {file}"
