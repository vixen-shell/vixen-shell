from typing import Literal, TypedDict, Callable
from abc import ABC, abstractmethod

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Log(TypedDict):
    level: LogLevel
    message: str


LogListener = Callable[[Log], None]


class AbsLogger(ABC):
    @abstractmethod
    def log(self, message: str, level: LogLevel = "INFO"):
        pass

    @abstractmethod
    def log_exception(
        self, e: Exception, level: Literal["WARNING", "ERROR"] = "WARNING"
    ):
        pass

    @abstractmethod
    def add_listener(self, listener: LogListener):
        pass

    @abstractmethod
    def remove_listener(self, listener: LogListener):
        pass


def get_logger_reference(logger):
    class LoggerReference(AbsLogger):
        def log(self, message: str, level: LogLevel = "INFO"):
            logger.log(message, level)

        def log_exception(
            self, e: Exception, level: Literal["WARNING"] | Literal["ERROR"] = "WARNING"
        ):
            logger.log_exception(e, level)

        def add_listener(self, listener: LogListener):
            logger.add_listener(listener)

        def remove_listener(self, listener: LogListener):
            logger.remove_listener(listener)

    return LoggerReference()
