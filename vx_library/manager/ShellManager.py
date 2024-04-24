from .logger import Logger


class ShellManager:
    @staticmethod
    def open():
        from ..shell import Shell

        try:
            Shell.open()
        except Shell.ShellException as exception:
            Logger.log(exception, "WARNING")
        except Exception:
            raise

    @staticmethod
    def close():
        from ..shell import Shell

        try:
            Shell.close()
            Logger.log("Exit Vixen Shell successfull")
        except Shell.ShellException as exception:
            Logger.log(exception, "WARNING")
        except Exception:
            raise

    @staticmethod
    def dev(dev_dir: str):
        from .utils import get_vite_process
        from ..shell import Shell

        try:
            vite_process = get_vite_process(dev_dir)
            dev_feature = Shell.init_dev_feature(dev_dir)
        except Shell.ShellException as exception:
            Logger.log(exception, "ERROR")
            return
        except Exception:
            raise

        vite_process.start()

        try:
            dev_feature.start()
            print(f"  \033[92m➜\033[0m  Vixen: start feature '{dev_feature.name}'")
        except Exception as exception:
            f"  \033[91m➜\033[0m  Vixen: {exception}"
            vite_process.terminate()

        if vite_process.is_alive:
            vite_process.join()

        try:
            Shell.stop_dev_feature()
        except Shell.ShellException as exception:
            Logger.log(exception, "WARNING")
        except Exception:
            raise
