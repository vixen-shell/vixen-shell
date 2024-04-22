class Manager:

    @staticmethod
    def init():
        from .vxm import vxm
        from .log import Logger

        Logger.init()
        return vxm

    @staticmethod
    def setup():
        from .setup import vx_setup
        from .log import Logger

        Logger.init()

        class SetupManager:
            @staticmethod
            def run(library_path: str):
                vx_setup(library_path)

            @staticmethod
            def warn(message: str):
                Logger.log("WARNING", message)

        return SetupManager
