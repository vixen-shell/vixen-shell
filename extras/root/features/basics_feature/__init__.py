from vx_root import root_feature, root_content
from .system import System

feature = root_feature()
content = root_content()

feature.init(
    {
        "autostart": True,
        "title": "Vixen Shell Basics",
        "frames": {
            "theme_settings": {
                "name": "Vixen Shell Theme Settings",
                "route": "vx_theme",
                "layer_frame": "disable",
            },
        },
    }
)

content.dispatch("data", "available_fonts")(System.Infos.available_fonts)
