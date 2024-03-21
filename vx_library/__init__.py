"""
Author            : Nohavye
Author's Email    : noha.poncelet@gmail.com
Repository        : https://github.com/vixen-shell/vixen-shell.git
Description       : vixen shell library.
License           : GPL3
"""


def init_setup():
    from .vx_manager import init_setup

    Setup, SetupTask, Commands = init_setup()
    return Setup, SetupTask, Commands


def init_vxm():
    from .vx_manager import init_vxm

    vxm = init_vxm()
    return vxm
