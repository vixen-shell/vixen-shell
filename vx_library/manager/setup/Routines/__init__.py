from .env_routines import (
    setup_environment,
    update_environment,
    install_environment_package,
    uninstall_environment_package,
    remove_all,
)
from .front_routines import setup_front, update_front
from .conf_routines import setup_config
from .feat_routines import vx_add_feature, vx_new_feature, vx_remove_feature


def setup(library_path: str):
    if not setup_environment(library_path):
        return False

    if not setup_front():
        return False

    return setup_config()


def update():
    if not update_environment():
        return False

    return update_front()
