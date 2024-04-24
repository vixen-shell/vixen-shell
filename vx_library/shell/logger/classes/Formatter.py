import logging, sys
from ....errorHandling import ErrorHandling
from ....cli import Cli


class Formatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.ERROR and "Traceback" in record.getMessage():
            ErrorHandling.excepthook(*sys.exc_info())
            return ""

        levelname = Cli.String.level(record.levelname, record.levelname)
        levelname += ":" + Cli.String.spaces(9 - len(record.levelname))

        return levelname + record.getMessage()
