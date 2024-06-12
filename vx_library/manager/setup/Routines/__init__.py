from .env_routines import (
    setup_environment,
    update_environment,
    install_environment_package,
    uninstall_environment_package,
    remove_all,
)
from .front_routines import setup_front, update_front
from .conf_routines import setup_config
from .feat_routines import (
    vx_add_feature,
    vx_add_extra_feature,
    vx_new_feature,
    vx_remove_feature,
)


def setup(library_path: str):
    from ...utils import get_vx_package_version, write_json

    result = setup_environment(library_path) and setup_front() and setup_config()

    if result:
        write_json(
            "/usr/share/vixen/vixen_setup.json",
            {"version": get_vx_package_version(library_path)},
        )

    return result


def update():
    return update_environment() and update_front()
