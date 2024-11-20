from vx_root import root_feature
from .system import System
from .theme_settings import theme_settings_frame

feature = root_feature()

feature.init(
    {
        "autostart": True,
        "title": "Vixen Shell Basics",
        "frames": {
            "theme_settings": theme_settings_frame,
        },
    }
)
