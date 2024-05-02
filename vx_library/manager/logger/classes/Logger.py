import logging

from .Formatter import Formatter
from ..utils import LogLevel


class Logger:
    logger = None

    @staticmethod
    def check_init(value: bool):
        def decorator(func):
            def wrapper(*args, **kwargs):
                if bool(Logger.logger) == value:
                    # @errorHandling exclude
                    return func(*args, **kwargs)
                else:
                    raise ValueError(
                        f"{Logger.__name__} not initialized"
                        if value
                        else f"{Logger.__name__} already initialized"
                    )

            return wrapper

        return decorator

    @staticmethod
    @check_init(False)
    def init():
        handler = logging.StreamHandler()
        handler.setFormatter(Formatter())

        logger = logging.getLogger("manager")
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

        Logger.logger = logger

    @staticmethod
    @check_init(True)
    def log(message: str, level: LogLevel = "INFO", suffix: str = None):
        message = f"{message} [{suffix}]" if suffix else message

        try:
            Logger.logger.log(logging._nameToLevel[level], message)
        except KeyError as error:
            raise KeyError(f"{error} is not a valid log level")
