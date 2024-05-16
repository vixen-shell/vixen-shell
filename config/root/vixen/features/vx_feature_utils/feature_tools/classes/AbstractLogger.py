from typing import Literal, TypedDict, Callable
from abc import ABC, abstractmethod

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Log(TypedDict):
    level: LogLevel
    message: str


LogListener = Callable[[Log], None]


class AbstractLogger(ABC):
    @staticmethod
    @abstractmethod
    def log(message: str, level: LogLevel):
        pass

    @staticmethod
    @abstractmethod
    def add_listener(listener: LogListener):
        pass

    @staticmethod
    @abstractmethod
    def remove_listener(listener: LogListener):
        pass
