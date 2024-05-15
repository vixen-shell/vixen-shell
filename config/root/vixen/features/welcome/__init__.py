from vx_feature_utils import define_feature

feature = define_feature(
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
        },
        "state": "disable",
    }
)

from .actions import *
from .data import *
