from .vxm_utils import sudo_is_used, close_api, api_is_running, open_api
from .setup import vx_remove
from .log import Logger

Logger.init()


class vxm:
    @staticmethod
    def remove():
        if not sudo_is_used():
            Logger.log("WARNING", "This command must be used with 'sudo'")
            return

        response = Logger.validate(
            "WARNING", "Are you sure you want to remove Vixen Shell?"
        )

        if response == "yes":
            if api_is_running():
                vxm.shell_close()
            vx_remove()

        if response == "no":
            Logger.log("INFO", "You made the right choice.")

    @staticmethod
    def shell_open():
        if not api_is_running():
            open_api()
        else:
            Logger.log("WARNING", "Vixen Shell Api is already running")

    @staticmethod
    def shell_close():
        if api_is_running():
            if close_api():
                Logger.log("INFO", "Exit Vixen Shell successfull")
            else:
                Logger.log("ERROR", "Unable to exit Vixen Shell")
        else:
            Logger.log("WARNING", "Vixen Shell Api is not running")
