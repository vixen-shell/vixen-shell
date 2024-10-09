from .logger import Logger

Logger.init()


class Manager:
    from .args_parser import handle_args
    from .SetupManager import SetupManager as Setup
