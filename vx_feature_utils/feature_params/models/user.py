from pydantic import BaseModel, ConfigDict
from collections import defaultdict
from .param import LayerFrameParams, LayerFrameParams_dict
from typing import TypedDict
from .types import *

# ---------------------------------------------- - - -
# MODELS
#


class user_FrameParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    template: str | None = None
    show_on_startup: bool | None = None
    layer_frame: LayerFrameParams | None = None


class user_FeatureParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    autostart: bool | None = None
    frames: dict[str, user_FrameParams] | None = None
    state: dict | None = None


# ---------------------------------------------- - - -
# DICT
#


class user_FrameParams_dict(TypedDict):
    template: str
    show_on_startup: bool
    layer_frame: LayerFrameParams_dict

    @staticmethod
    def get_structure():
        return {
            "template": "VALUE",
            "show_on_startup": "VALUE",
            "layer_frame": LayerFrameParams_dict.get_structure(),
        }


class user_FeatureParams_dict(TypedDict):
    autostart: bool
    frames: dict[str, user_FrameParams_dict]
    state: dict

    @staticmethod
    def get_structure():
        return {
            "autostart": "VALUE",
            "frames": defaultdict(lambda: user_FrameParams_dict.get_structure()),
            "state": "VALUE",
        }
