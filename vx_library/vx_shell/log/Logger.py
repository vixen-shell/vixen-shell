import logging
from typing import TypedDict, List, Literal, Callable, Optional, Dict

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class LogData(TypedDict):
    type: Literal["TEXT", "DATA"]
    content: str | Dict[str, str | int | float | bool]
    asset: Optional[str]


class Log(TypedDict):
    level: LogLevel
    purpose: str
    data: Optional[LogData]


LogListener = Callable[[Log], None]


class Logger:
    uvicorn_serve = False
    cache_size = 512
    log_data: LogData = None
    log_cache: List[Log] = []
    log_listeners: List[LogListener] = []

    @staticmethod
    def init():
        class LogHandler(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                data, Logger.log_data = Logger.log_data, None
                log = Logger.cache(record.levelname, record.getMessage(), data)

                for listener in Logger.log_listeners:
                    listener(log)

        def addLoggerHandler(name: str):
            logger = logging.getLogger(name)
            logger.addHandler(LogHandler())

        addLoggerHandler("uvicorn")
        # addLoggerHandler('uvicorn.access')

    @staticmethod
    def cache(level: LogLevel, purpose: str, data: Optional[LogData] = None) -> Log:
        if not Logger.uvicorn_serve:
            if purpose.startswith("Uvicorn running on"):
                purpose = purpose.replace("Uvicorn", "Vixen API").replace(
                    " (Press CTRL+C to quit)", ""
                )
                Logger.uvicorn_serve = True

        if len(Logger.log_cache) == Logger.cache_size:
            Logger.log_cache.pop(0)

        log = Log(level=level, purpose=purpose, data=data)

        Logger.log_cache.append(log)
        return log

    @staticmethod
    def log(level: LogLevel, message: str, data: Optional[Dict] = None):
        logger = logging.getLogger("uvicorn")
        Logger.log_data = data

        if level == "DEBUG":
            logger.debug(message)
        if level == "INFO":
            logger.info(message)
        if level == "WARNING":
            logger.warning(message)
        if level == "ERROR":
            logger.error(message)
        if level == "CRITICAL":
            logger.critical(message)

    @staticmethod
    def add_log_listener(listener: LogListener):
        Logger.log_listeners.append(listener)

    @staticmethod
    def remove_log_listener(listener: LogListener):
        Logger.log_listeners.remove(listener)
