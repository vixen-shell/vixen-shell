def init_setup():
    from .setup import Setup, SetupTask, Commands
    from .log import Logger

    Logger.init()

    return Setup, SetupTask, Commands


def init_vxm():
    import requests
    from .setup import Setup, SetupTask, Commands
    from .log import Logger
    from ..vx_shell import api

    Logger.init()

    VX_ENV_PATH = "/opt/vixen-env"

    class vxm:
        @staticmethod
        def api_is_running() -> bool:
            try:
                response = requests.get("http://localhost:6481/ping")

                if response.status_code == 200:
                    return True
                else:
                    return False

            except requests.RequestException:
                return False

        @staticmethod
        def open_api():
            if not vxm.api_is_running():
                api.run()
            else:
                Logger.log("WARNING", "Vixen Shell Api is already running")

        @staticmethod
        def close_api():
            def close() -> bool:
                try:
                    response = requests.get("http://localhost:6481/shutdown")

                    if response.status_code == 200:
                        return True
                    else:
                        return False

                except requests.RequestException:
                    return False

            if vxm.api_is_running():
                if close():
                    Logger.log("INFO", "Exit Vixen Shell successfull")
                else:
                    Logger.log("ERROR", "Unable to exit Vixen Shell")
            else:
                Logger.log("WARNING", "Vixen Shell Api is not running")

    return vxm
