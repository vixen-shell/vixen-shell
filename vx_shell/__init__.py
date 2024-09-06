"""
Author            : Nohavye
Author's Email    : noha.poncelet@gmail.com
Repository        : https://github.com/vixen-shell/vixen-shell.git
Description       : vixen shell api library.
License           : GPL3
"""


def run_shell():
    from sys import path
    from .api import api
    from .servers import ApiServer
    from .ImportHook import ImportHook

    ImportHook.init()

    path.append("/usr/share/vixen/features")
    ApiServer.start(api)
