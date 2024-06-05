from typing import TypedDict, List, Callable, Optional

from ...logger import Logger
from ....cli import Cli


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
        command: str,
        undo_command: str = None,
        requirements: List[Requirement] = None,
        skip_on: Skipper = None,
        spinner: bool = True,
    ):
        self.is_done = False
        self.is_skipped = False
        self.purpose = purpose
        self.command = command
        self.undo_command = undo_command
        self.requirements = requirements
        self.skip_on = skip_on
        self.spinner = Cli.Spinner() if spinner else None

    def set_spinner(self, is_running: bool):
        if self.spinner:
            if is_running:
                self.spinner.run()
            else:
                self.spinner.stop()

    def check_requirements(self) -> bool:
        if self.requirements:
            Logger.log(self.purpose, suffix="CHECKS")

            for requirement in self.requirements:
                if not requirement["callback"]():
                    if not requirement.get("issue"):
                        Logger.log(requirement["failure_message"], "ERROR")
                        return False
                    else:
                        Logger.log(requirement["failure_message"], "WARNING")
                        issue = requirement["issue"]

                        if Cli.exec(issue["command"]):
                            Logger.log(issue["purpose"], "WARNING", "ISSUE")
                        else:
                            Logger.log("Unable to apply issue", "ERROR", "ISSUE")
                            return False

                Logger.log(requirement["purpose"], suffix="OK")

        return True

    def exec(self) -> bool:
        Logger.log(self.purpose + " ...")

        if not self.check_requirements():
            Logger.log(self.purpose, "WARNING", "FAILED")
            return False

        self.set_spinner(True)

        if self.skip_on and self.skip_on["callback"]():
            Logger.log(
                f"{self.purpose}: {self.skip_on['message']}", "WARNING", "SKIPPED"
            )

            self.is_skipped = True
            self.is_done = True

        if not self.is_done:
            self.is_done = Cli.exec(self.command)

        self.set_spinner(False)

        if not self.is_skipped:
            Logger.log(
                self.purpose,
                "INFO" if self.is_done else "ERROR",
                "DONE" if self.is_done else "FAILED",
            )

        return self.is_done

    def undo(self) -> bool:
        if not self.undo_command or self.is_skipped:
            return True

        result = True
        status = "NOT DONE"
        level = "WARNING"

        if self.is_done:
            result = Cli.exec(self.undo_command)
            status = "UNDO" if result else "UNDO FAILED"
            level = "WARNING" if result else "ERROR"

        Logger.log(self.purpose, level, status)
        self.is_done = not result
        return result
