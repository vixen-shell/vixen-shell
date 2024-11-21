from vx_root import root_feature
from .theme_settings import theme_settings_frame
from .exports import *

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
