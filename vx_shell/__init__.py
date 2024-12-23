"""
Author            : Nohavye
Author's Email    : noha.poncelet@gmail.com
Repository        : https://github.com/vixen-shell/vixen-shell.git
Description       : vixen shell api library.
License           : GPL3
"""

from .servers import AsyncLoop


def run_shell():
    from sys import path
    from vx_path import VxPath
    from vx_config import VxConfig

    from .api import api
    from .servers import ApiServer
    from .ImportHook import ImportHook

    ImportHook.init()
    VxConfig.load()

    path.append(VxPath.ROOT_FEATURE_MODULES)
    ApiServer.start(api)
