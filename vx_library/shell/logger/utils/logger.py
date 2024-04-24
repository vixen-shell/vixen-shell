from typing import TypedDict, Callable
from ....cli import Cli

LogLevel = Cli.Level


class Log(TypedDict):
    level: LogLevel
    message: str


LogListener = Callable[[Log], None]
