from vx_path import VxPath
from .env_routines import (
    setup_environment,
    update_environment,
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

    result = (
        setup_environment(library_path) and setup_front() and setup_config(library_path)
    )

    if result:
        write_json(
            VxPath.VX_SETUP_FILE,
            {"version": get_vx_package_version(library_path)},
        )
    else:
        remove_all()

    return result


def update():
    return update_environment() and update_front()
