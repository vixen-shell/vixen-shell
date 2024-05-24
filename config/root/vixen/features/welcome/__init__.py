from vx_feature_utils import Utils

utils = Utils.define_feature_utils()
content = Utils.define_feature_content(
    {
        "frames": {
            "main": {
                "name": "Welcome to Vixen Shell",
                "route": "main",
                "layer_frame": "disable",
            },
            "about": {
                "name": "About Vixen Shell",
                "route": "about",
                "layer_frame": {
                    "monitor_id": 2,
                },
            },
        }
    }
)

from .actions import *
from .data import *
