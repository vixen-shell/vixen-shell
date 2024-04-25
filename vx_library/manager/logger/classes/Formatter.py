import logging
from ..utils import Cli


class Formatter(logging.Formatter):
    def format(self, record):
        levelname = Cli.String.level(record.levelname, record.levelname)
        levelname += ":" + Cli.String.spaces(9 - len(record.levelname))
        message = Cli.String.level_brackets(record.getMessage(), record.levelname)

        return levelname + message
