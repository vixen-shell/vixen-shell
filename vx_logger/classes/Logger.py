import logging, traceback
from typing import Literal
from .Formatter import FormatterFilter, Formatter, DevFormatter
from ..utils import Log, LogLevel, LogListener


class Logger:
    logger: logging.Logger = None
    log_listeners: list[LogListener] = []
    log_handlers: dict[str, logging.FileHandler] = {}
    tty_print = None

    @staticmethod
    def check_init(value: bool):
        def decorator(func):
            def wrapper(*args, **kwargs):
                if bool(Logger.logger) == value:
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
        logger = logging.getLogger("uvicorn")

        class LogHandler(logging.StreamHandler):
            def emit(self, record: logging.LogRecord) -> None:
                log = Log(level=record.levelname, message=record.getMessage())

                for listener in Logger.log_listeners:
                    listener(log)

        formatter_handler = logging.StreamHandler()
        formatter_handler.addFilter(FormatterFilter())
        formatter_handler.setFormatter(Formatter())

        logger.setLevel(logging.DEBUG)
        logger.addHandler(formatter_handler)
        logger.addHandler(LogHandler())
        Logger.logger = logger

    @staticmethod
    @check_init(True)
    def print(*values: object):
        if Logger.tty_print:
            with open(Logger.tty_print, "w") as tty:
                return print(*values, file=tty)

        print(*values)

    @staticmethod
    @check_init(True)
    def debug(*values: object):
        message = " ".join(map(repr, values))
        Logger.log(message, "DEBUG")

    @staticmethod
    @check_init(True)
    def log(message: str, level: LogLevel = "INFO"):
        try:
            Logger.logger.log(logging._nameToLevel[level], message)
        except KeyError as error:
            raise KeyError(f"{error} is not a valid log level")

    @staticmethod
    @check_init(True)
    def log_exception(e: Exception, level: Literal["WARNING", "ERROR"] = "WARNING"):
        title_exception = f"{e}\n"
        type_exception = f"[Type]: {type(e)}\n"

        tb_last = traceback.extract_tb(e.__traceback__)[-1]

        file_exception = f"[File]: {tb_last.filename} [line]: {tb_last.lineno}\n"
        code_exception = f"[Code]: {tb_last.line}"

        Logger.log(
            title_exception + type_exception + file_exception + code_exception, level
        )

    @staticmethod
    @check_init(True)
    def add_handler(tty_path: str, dev_mode: bool = False):
        file_handler = logging.FileHandler(tty_path)
        file_handler.setLevel(logging.DEBUG)

        if dev_mode:
            Logger.tty_print = tty_path

            class LevelFilter(logging.Filter):
                def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
                    return record.levelno in (
                        logging.DEBUG,
                        logging.WARNING,
                        logging.ERROR,
                        logging.CRITICAL,
                    )

            file_handler.addFilter(LevelFilter())
            file_handler.setFormatter(DevFormatter())

        else:
            file_handler.setFormatter(Formatter())

        Logger.log_handlers[tty_path] = file_handler
        Logger.logger.addHandler(file_handler)

    @staticmethod
    @check_init(True)
    def remove_handler(tty_path: str):
        file_handler = Logger.log_handlers.get(tty_path)

        if file_handler:
            if Logger.tty_print == tty_path:
                Logger.tty_print = None

            Logger.logger.removeHandler(file_handler)
            Logger.log_handlers.pop(tty_path)

    @staticmethod
    def add_listener(listener: LogListener):
        Logger.log_listeners.append(listener)

    @staticmethod
    def remove_listener(listener: LogListener):
        Logger.log_listeners.remove(listener)
