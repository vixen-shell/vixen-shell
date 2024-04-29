"""
Author            : Nohavye
Author's Email    : noha.poncelet@gmail.com
Repository        : https://github.com/vixen-shell/vixen-shell.git
Description       : vixen shell api library.
License           : GPL3
"""


class Shell:
    from .requests import ApiRequests as Requests

    class ShellException(Exception):
        def __init__(self, message: str):
            super().__init__(message)

    @staticmethod
    def is_open():
        return Shell.Requests.ping()

    @staticmethod
    def open():
        if Shell.is_open():
            raise Shell.ShellException("Vixen Shell is already running")

        from .api import api
        from .servers import ApiServer

        ApiServer.start(api)

    @staticmethod
    def close():
        if not Shell.is_open():
            raise Shell.ShellException("Vixen Shell is not running")

        Shell.Requests.close()

    @staticmethod
    def init_dev_feature(dev_dir: str):
        if not Shell.is_open():
            raise Shell.ShellException("Vixen Shell is not running")

        try:

            class FeatureReference:
                def __init__(self, name: str):
                    self.name = name

                def start(self):
                    try:
                        Shell.Requests.start_feature(self.name)
                    except Exception:
                        raise

            return FeatureReference(Shell.Requests.init_dev_feature(dev_dir))

        except Exception:
            raise

    @staticmethod
    def stop_dev_feature():
        if not Shell.is_open():
            raise Shell.ShellException("Vixen Shell is not running")

        try:
            Shell.Requests.stop_dev_feature()
        except Exception as exception:
            raise exception

    @staticmethod
    def feature_names() -> list[str]:
        if not Shell.is_open():
            raise Shell.ShellException("Vixen Shell is not running")

        return Shell.Requests.feature_names()
