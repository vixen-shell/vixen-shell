from .utils import use_sudo


class ShellManager:
    @staticmethod
    @use_sudo(False)
    def open():
        from .requests import ShellRequests

        ShellRequests.open()

    @staticmethod
    @use_sudo(False)
    def close():
        from .requests import ShellRequests

        ShellRequests.close()

    @staticmethod
    @use_sudo(False)
    def dev(directory: str):
        from .requests import ShellRequests
        from .utils import get_vite_process

        feature_name = ShellRequests.load_feature(directory)
        if not feature_name:
            return

        vite_process = get_vite_process(directory)
        if not vite_process:
            return

        vite_process.start()

        if ShellRequests.start_feature(feature_name):
            print(f"  \033[92m➜\033[0m  Vixen: start feature '{feature_name}'")
            vite_process.join()
        else:
            print(
                f"  \033[31m➜\033[0m  Vixen: Error on starting feature '{feature_name}'"
            )
            vite_process.terminate()

        if ShellRequests.ping():
            ShellRequests.unload_feature(feature_name)

    @staticmethod
    @use_sudo(False)
    def feature_names():
        from .requests import ShellRequests

        print(ShellRequests.feature_names())
