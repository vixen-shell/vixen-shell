import logging, re
from ..utils import Cli


class Formatter(logging.Formatter):
    def format(self, record):
        levelname = Cli.String.level(record.levelname, record.levelname)
        levelname += ":" + Cli.String.spaces(9 - len(record.levelname))
        message = record.getMessage()

        suffix = re.findall(r"\[(.*?)\]", message)
        suffix = suffix[0] if suffix else ""

        if suffix:
            message = message.replace(f"[{suffix}]", "")
            suffix = Cli.String.level(f"[{suffix}]", record.levelname)

        return levelname + message + suffix
