def init_setup():
    from .setup import vx_setup
    from .log import Logger

    Logger.init()

    return vx_setup


def init_vxm():
    from .vxm import vxm
    from .log import Logger

    Logger.init()

    return vxm
