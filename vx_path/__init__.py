import os


class VxPath:
    env_name: str = "vixen-env"
    ENV_PARENT: str = "/opt"
    ENV: str = f"{ENV_PARENT}/{env_name}"

    front_name: str = "vx-front-main"
    FRONT_PARENT: str = "/var/opt"
    FRONT: str = f"{FRONT_PARENT}/{front_name}"
    FRONT_SOURCES: str = f"{FRONT}/src"
    FRONT_FEATURES: str = f"{FRONT_SOURCES}/features"
    FRONT_DIST: str = f"{FRONT}/dist"

    ROOT_CONFIG_PARENT: str = "/usr/share"
    ROOT_CONFIG: str = f"{ROOT_CONFIG_PARENT}/vixen"
    ROOT_FEATURE_MODULES: str = f"{ROOT_CONFIG}/features"
    ROOT_PHOSPHOR_ICONS: str = f"{ROOT_CONFIG}/phosphor"

    USER_CONFIG_PARENT: str = f"/home/{os.getlogin()}/.config"
    USER_CONFIG: str = f"{USER_CONFIG_PARENT}/vixen"
    USER_FEATURE_PARAMS: str = f"{USER_CONFIG}/features"

    VX_SETUP_FILE: str = f"{ROOT_CONFIG}/vixen_setup.json"
    VX_CONFIG_FILE: str = f"{USER_CONFIG}/vixen.json"

    DESKTOP_ENTRIES: str = "/usr/share/applications"
