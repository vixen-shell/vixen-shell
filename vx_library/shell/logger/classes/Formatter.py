import logging, sys
from ..utils import Cli, ErrorHandling


class Formatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.ERROR and "Traceback" in record.getMessage():
            ErrorHandling.excepthook(*sys.exc_info())
            return str()

        levelname = Cli.String.level(record.levelname, record.levelname)
        levelname += ":" + Cli.String.spaces(9 - len(record.levelname))

        return levelname + record.getMessage()
