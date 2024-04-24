from .logger import Logger

Logger.init()


class Manager:
    from .ShellManager import ShellManager as Shell
    from .SetupManager import SetupManager as Setup
