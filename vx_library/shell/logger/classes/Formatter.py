import logging
from ..utils import Cli, ErrorHandling


class Formatter(logging.Formatter):
    def format(self, record):
        message = record.getMessage()

        if record.levelno == logging.ERROR:
            if "Traceback" in message or "Exception in ASGI application" in message:
                ErrorHandling.print_error()
                return str()

            if message == "Application startup failed. Exiting.":
                ErrorHandling.sys_exit()

        levelname = Cli.String.level(record.levelname, record.levelname)
        levelname += ":" + Cli.String.spaces(9 - len(record.levelname))
        message = Cli.String.level_brackets(message, "DEBUG")

        return levelname + message
