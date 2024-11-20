import logging
from ..utils import Cli


class FormatterFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return record.name != "uvicorn.access"


class Formatter(logging.Formatter):
    def format(self, record):
        message = record.getMessage()

        if record.levelno == logging.ERROR:
            if message == "Application startup failed. Exiting.":
                Cli.exec("killall --signal KILL vxm")

        levelname = Cli.String.level(record.levelname, record.levelname)
        levelname += ":" + Cli.String.spaces(9 - len(record.levelname))
        message = Cli.String.level_brackets(message, "DEBUG")

        return levelname + message


class DevFormatter(logging.Formatter):
    def format(self, record):
        message = record.getMessage()

        levelname = Cli.String.level(record.levelname, record.levelname)
        levelname += ":" + Cli.String.spaces(9 - len(record.levelname))
        message = Cli.String.level_brackets(message, "DEBUG")

        return "\n" + levelname + message + "\n"
