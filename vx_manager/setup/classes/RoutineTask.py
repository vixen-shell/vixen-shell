from typing import TypedDict, List, Callable, Optional

from ...logger import Logger
from vx_cli import Cli


class Issue(TypedDict):
    purpose: str
    command: str


class Requirement(TypedDict):
    purpose: str
    callback: Callable[[], bool]
    failure_message: str
    issue: Optional[Issue]


class Skipper(TypedDict):
    callback: Callable[[], bool]
    message: str


class RoutineTask:
    def __init__(
        self,
        purpose: str,
        command: str | Callable[[], bool],
        undo_command: str | Callable[[], bool] = None,
        requirements: List[Requirement] = None,
        skip_on: Skipper = None,
        show_output: bool = False,
        spinner: bool = True,
    ):
        self.is_done = False
        self.is_skipped = False
        self.purpose = purpose
        self.command = command
        self.undo_command = undo_command
        self.requirements = requirements
        self.skip_on = skip_on
        self.show_output = show_output
        self.spinner = Cli.Spinner() if spinner and not show_output else None

    def set_spinner(self, is_running: bool):
        if self.spinner:
            if is_running:
                self.spinner.run()
            else:
                self.spinner.stop()

    def check_requirements(self) -> bool:
        if self.requirements:
            Logger.log(self.purpose, suffix="CHECKS", above=True)

            for requirement in self.requirements:
                if not requirement["callback"]():
                    if not requirement.get("issue"):
                        Logger.log(requirement["failure_message"], "ERROR")
                        return False
                    else:
                        Logger.log(requirement["failure_message"], "WARNING")
                        issue = requirement["issue"]

                        if Cli.exec(issue["command"]):
                            Logger.log(issue["purpose"], "WARNING", "ISSUE", above=True)
                        else:
                            Logger.log("Unable to apply issue", "ERROR", "ISSUE")
                            return False

                Logger.log(requirement["purpose"], suffix="OK", above=True)

        return True

    def exec(self) -> bool:
        Logger.log(self.purpose + " ...")

        if not self.check_requirements():
            Logger.log(self.purpose, "WARNING", "FAILED")
            return False

        self.set_spinner(True)

        if self.skip_on and self.skip_on["callback"]():
            Logger.log(
                f"{self.purpose}: {self.skip_on['message']}",
                "WARNING",
                "SKIPPED",
                above=True,
            )

            self.is_skipped = True
            self.is_done = True

        if not self.is_done:
            if self.show_output:
                print()

            if isinstance(self.command, str):
                self.is_done = Cli.exec(self.command, self.show_output)
            if callable(self.command):
                self.is_done = self.command()

            if self.show_output:
                print()

        self.set_spinner(False)

        if not self.is_skipped:
            Logger.log(
                self.purpose,
                "INFO" if self.is_done else "ERROR",
                "DONE" if self.is_done else "FAILED",
                above=True if self.is_done and not self.show_output else False,
            )

        return self.is_done

    def undo(self) -> bool:
        if not self.undo_command or self.is_skipped:
            return True

        result = True
        status = "NOT DONE"
        level = "WARNING"

        if self.is_done:
            if isinstance(self.undo_command, str):
                result = Cli.exec(self.undo_command)
            if callable(self.undo_command):
                result = self.undo_command()

            status = "UNDO" if result else "UNDO FAILED"
            level = "WARNING" if result else "ERROR"

        Logger.log(self.purpose, level, status)
        self.is_done = not result
        return result
