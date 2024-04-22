"""
Author            : Nohavye
Author's Email    : noha.poncelet@gmail.com
Repository        : https://github.com/vixen-shell/vixen-shell.git
Description       : vixen shell library.
License           : GPL3
"""


def init_setup():
    from .manager import init_setup

    return init_setup()


def init_vxm():
    from .manager import init_vxm

    vxm = init_vxm()
    return vxm
