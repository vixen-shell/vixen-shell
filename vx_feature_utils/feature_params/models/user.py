from pydantic import BaseModel, ConfigDict
from collections import defaultdict
from typing import TypedDict
from .types import *

# ---------------------------------------------- - - -
# MODELS
#


class user_MarginParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    top: int | None = None
    right: int | None = None
    bottom: int | None = None
    left: int | None = None


class user_LayerFrameParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    monitor_id: int | None = None
    auto_exclusive_zone: bool | None = None
    exclusive_zone: int | None = None
    level: LevelKeys | None = None
    anchor_edge: AnchorEdgeKeys | None = None
    alignment: AlignmentKeys | None = None
    margins: user_MarginParams | None = None
    width: int | None = None
    height: int | None = None


class user_FrameParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    template: str | None = None
    show_on_startup: bool | None = None
    layer_frame: user_LayerFrameParams | None = None


class user_FeatureParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    autostart: bool | None = None
    frames: dict[str, user_FrameParams] | None = None
    state: dict | None = {}


# ---------------------------------------------- - - -
# DICT
#


class user_MarginParams_dict(TypedDict):
    top: int
    right: int
    bottom: int
    left: int

    @staticmethod
    def get_structure():
        return {
            "top": "VALUE",
            "right": "VALUE",
            "bottom": "VALUE",
            "left": "VALUE",
        }


class user_LayerFrameParams_dict(TypedDict):
    monitor_id: int
    auto_exclusive_zone: bool
    exclusive_zone: int
    level: LevelKeys
    anchor_edge: AnchorEdgeKeys
    alignment: AlignmentKeys
    margins: user_MarginParams_dict
    width: int
    height: int

    @staticmethod
    def get_structure():
        return {
            "monitor_id": "VALUE",
            "auto_exclusive_zone": "VALUE",
            "exclusive_zone": "VALUE",
            "level": "VALUE",
            "anchor_edge": "VALUE",
            "alignment": "VALUE",
            "margins": user_MarginParams_dict.get_structure(),
            "width": "VALUE",
            "height": "VALUE",
        }


class user_FrameParams_dict(TypedDict):
    template: str
    show_on_startup: bool
    layer_frame: user_LayerFrameParams_dict

    @staticmethod
    def get_structure():
        return {
            "template": "VALUE",
            "show_on_startup": "VALUE",
            "layer_frame": user_LayerFrameParams_dict.get_structure(),
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
