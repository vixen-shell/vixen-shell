import os


class DevMode:
    is_active: bool = False

    @staticmethod
    def set(is_active: bool):
        DevMode.is_active = is_active


HOME_DIRECTORY = os.path.expanduser("~")
VX_CONFIG_DIRECTORY = f"{HOME_DIRECTORY}/.config/vixen"
FEATURE_SETTINGS_DIRECTORY = f"{VX_CONFIG_DIRECTORY}/features"
DEFAULT_FEATURES_CONFIG_FILE = f"{VX_CONFIG_DIRECTORY}/default_features.json"


def get_front_url():
    FRONT_URL = "http://localhost:6492"
    DEV_FRONT_URL = "http://localhost:5173"
    return DEV_FRONT_URL if DevMode.is_active else FRONT_URL
