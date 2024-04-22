import logging, sys, time, threading
from typing import Literal, TypedDict, List

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


COLORS = {
    "DEBUG": "\033[36m",  # Cyan
    "INFO": "\033[32m",  # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",  # Red
    "CRITICAL": "\033[91m",  # Bright Red
    "RESET": "\033[0m",  # Reset to default color
}


class ExcludeAnswers(TypedDict):
    answers: list
    reason: str


class Logger:
    is_init = False

    @staticmethod
    def init(level: int = logging.INFO):
        if not Logger.is_init:

            class Formatter(logging.Formatter):

                def format(self, record):
                    levelname = record.levelname
                    color = COLORS.get(levelname, COLORS["RESET"])
                    record.levelname = f"{color}{levelname}{COLORS['RESET']}:" + (
                        " " * (10 - len(levelname))
                    )
                    message = super().format(record)
                    return message

            logger = logging.getLogger("vixen")

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(Formatter("%(levelname)s %(message)s"))

            logger.addHandler(console_handler)
            logger.setLevel(level)

            Logger.is_init = True

    @staticmethod
    def log(level: LogLevel, message: str, prefix: str = None):
        if not Logger.is_init:
            raise Exception("Logger is not initialized !")
        else:
            logger = logging.getLogger("vixen")

            if prefix:
                color = COLORS.get(level, COLORS["RESET"])
                message = f"{message} {color}[{prefix}]{COLORS['RESET']}"

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
    def validate(level: LogLevel, question: str) -> Literal["yes", "no"]:
        Logger.log(level, f"{question}")

        try:
            while True:
                response = input("(yes/no or [ctrl + C]): ").strip().lower()

                if response in ["yes", "no"]:
                    return response
                else:
                    Logger.log("INFO", "Please answer with 'yes' or 'no'.")
        except KeyboardInterrupt:
            print()
            return "no"

    @staticmethod
    def question(
        level: LogLevel,
        question: str,
        exclude_answers: List[ExcludeAnswers] = [],
    ) -> str | None:
        def check_exclude_reasons(response: str):
            for exclude in exclude_answers:
                if response in exclude["answers"]:
                    reason = exclude.get("reason")
                    if reason:
                        Logger.log("WARNING", reason)

        def check_validity(response: str) -> bool:
            for exclude in exclude_answers:
                if response in exclude["answers"]:
                    Logger.log("WARNING", f"'{response}' is not a valid answer")
                    return False
            return True

        Logger.log(level, f"{question}")

        try:
            while True:
                response = (
                    input("(type or [ctrl + C]): ").strip().lower().replace(" ", "")
                )

                validity = check_validity(response)

                if response and validity:
                    return response
                else:
                    if response:
                        check_exclude_reasons(response)
                    Logger.log("INFO", "Please type your answer.")

        except KeyboardInterrupt:
            print()
            return

    class Spinner:
        def __init__(self):
            self.is_running = False
            self.thread = threading.Thread(target=self.spinner)

        def spinner(self):
            self.is_running = True
            n_point: int = 0

            def remove_point(n_point: int) -> int:
                sys.stdout.write("\b" * n_point)
                sys.stdout.write(" " * n_point)
                sys.stdout.write("\b" * n_point)
                sys.stdout.flush()
                return 0

            def add_point(n_point: int) -> int:
                sys.stdout.write(".")
                sys.stdout.flush()
                return n_point + 1

            def handle_point(n_point: int) -> int:
                if self.is_running and n_point < 3:
                    n_point = add_point(n_point)
                else:
                    n_point = remove_point(n_point)

                return n_point

            while True:
                if not self.is_running:
                    remove_point(n_point)
                    break
                else:
                    time.sleep(0.5)
                    n_point = handle_point(n_point)

        def cursor(self, visible: bool):
            if not visible:
                sys.stdout.write("\033[?25l")
                sys.stdout.flush()
            else:
                sys.stdout.write("\033[?25h")
                sys.stdout.flush()

        def run(self):
            if not self.is_running:
                self.cursor(False)
                self.thread.start()

        def stop(self):
            if self.is_running:
                self.is_running = False
                sys.stdout.write("\r")
                sys.stdout.flush()
                self.cursor(True)
                self.thread.join()
