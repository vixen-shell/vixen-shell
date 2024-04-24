import logging
from .Formatter import Formatter
from ..utils.logger import Log, LogLevel, LogListener
from ....cli import Cli


class Logger:
    logger = None
    cache_size = 512
    log_cache: list[Log] = []
    log_listeners: list[LogListener] = []

    @staticmethod
    def check_init(value: bool):
        def decorator(func):
            def wrapper(*args, **kwargs):
                if bool(Logger.logger) == value:
                    return func(*args, **kwargs)  # @errorHandling exclude
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
        logger = logging.getLogger("uvicorn")

        class LogHandler(logging.StreamHandler):
            def emit(self, record: logging.LogRecord) -> None:
                log = Log(level=record.levelname, message=record.getMessage())

                if len(Logger.log_cache) == Logger.cache_size:
                    Logger.log_cache.pop(0)

                Logger.log_cache.append(log)

                for listener in Logger.log_listeners:
                    listener(log)

                if (
                    record.levelno == logging.ERROR
                    and record.getMessage() == "Application startup failed. Exiting."
                ):
                    Cli.exec("killall --signal KILL vxm")

        formatter_handler = logging.StreamHandler()
        formatter_handler.setFormatter(Formatter())

        logger.addHandler(formatter_handler)
        logger.addHandler(LogHandler())
        Logger.logger = logger

    @staticmethod
    @check_init(True)
    def log(message: str, level: LogLevel = "INFO"):
        try:
            Logger.logger.log(logging._nameToLevel[level], message)
        except KeyError as error:
            raise KeyError(f"{error} is not a valid log level")

    @staticmethod
    def add_listener(listener: LogListener):
        Logger.log_listeners.append(listener)

    @staticmethod
    def remove_listener(listener: LogListener):
        Logger.log_listeners.remove(listener)
