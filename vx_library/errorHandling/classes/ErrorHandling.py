import sys

from .ErrorSummary import ErrorSummary


class ErrorHandling:
    is_init: bool = False
    excepthook = None

    @staticmethod
    def check_init(value: bool):
        def decorator(func):
            def wrapper(*args, **kwargs):
                if ErrorHandling.is_init == value:
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
        def custom_excepthook(exc_type, exc_value, exc_traceback):
            ErrorSummary(exc_type, exc_value, exc_traceback).print(path_filter)

        sys.excepthook = custom_excepthook
        ErrorHandling.excepthook = custom_excepthook
        ErrorHandling.is_init = True
