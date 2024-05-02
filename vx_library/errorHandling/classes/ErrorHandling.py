import sys

from .ErrorSummary import ErrorSummary
from ...cli import Cli


class ErrorHandling:
    get_excepthook = None

    @staticmethod
    def check_init(value: bool):
        def decorator(func):
            def wrapper(*args, **kwargs):
                if bool(ErrorHandling.get_excepthook) == value:
                    return func(*args, **kwargs)
                else:
                    raise ValueError(
                        f"{ErrorHandling.__name__} not initialized"
                        if value
                        else f"{ErrorHandling.__name__} already initialized"
                    )

            return wrapper

        return decorator

    @staticmethod
    @check_init(False)
    def init(path_filter: str = None):
        def get_excepthook(sys_exit):
            def hook(exc_type, exc_value, exc_traceback):
                ErrorSummary(exc_type, exc_value, exc_traceback).print(path_filter)

                if sys_exit:
                    ErrorHandling.sys_exit()

            return hook

        sys.excepthook = get_excepthook(False)
        ErrorHandling.get_excepthook = get_excepthook

    @staticmethod
    @check_init(True)
    def print_error(sys_exit: bool = False):
        ErrorHandling.get_excepthook(sys_exit)(*sys.exc_info())

    @staticmethod
    @check_init(True)
    def sys_exit():
        Cli.exec("killall --signal KILL vxm")
