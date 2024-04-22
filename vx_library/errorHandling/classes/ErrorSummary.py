from types import TracebackType
from typing import Type
from builtins import BaseException

from .CallStack import CallStack
from ...cli import Cli


class ErrorSummary:
    def __init__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        exc_traceback: TracebackType,
    ):
        self.type = exc_type.__name__
        self.message = str(exc_value)
        self.stack = CallStack(exc_traceback)

    def print(self, path_filter: str = None):
        print(
            Cli.String.format(
                string=Cli.String.level(self.message, "WARNING"),
                prefix=Cli.String.level(f"\n[ERROR] {self.type}: ", "ERROR"),
            )
        )

        self.stack.print(path_filter)
