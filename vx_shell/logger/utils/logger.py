from typing import TypedDict, Callable
from vx_cli import Cli

LogLevel = Cli.Level


class Log(TypedDict):
    level: LogLevel
    message: str


LogListener = Callable[[Log], None]
