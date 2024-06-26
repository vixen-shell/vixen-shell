from pydantic import BaseModel, ConfigDict
from typing import TypedDict
from .types import *

# ---------------------------------------------- - - -
# MODELS
#


class MarginParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    top: int | None = None
    right: int | None = None
    bottom: int | None = None
    left: int | None = None


class LayerFrameParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    monitor_id: int | None = None
    auto_exclusive_zone: bool | None = None
    exclusive_zone: int | None = None
    level: LevelKeys | None = None
    anchor_edge: AnchorEdgeKeys | None = None
    alignment: AlignmentKeys | None = None
    margins: MarginParams | None = None
    width: int | None = None
    height: int | None = None


class FrameParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    route: str
    show_on_startup: bool | None = None
    layer_frame: LayerFrameParams | None = None


# ---------------------------------------------- - - -
# DICT
#


class MarginParams_dict(TypedDict):
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


class LayerFrameParams_dict(TypedDict):
    monitor_id: int
    auto_exclusive_zone: bool
    exclusive_zone: int
    level: LevelKeys
    anchor_edge: AnchorEdgeKeys
    alignment: AlignmentKeys
    margins: MarginParams_dict
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
            "margins": MarginParams_dict.get_structure(),
            "width": "VALUE",
            "height": "VALUE",
        }


class FrameParams_dict(TypedDict):
    name: str
    route: str
    show_on_startup: bool
    layer_frame: LayerFrameParams_dict


from .root import root_FeatureParams_dict
from .user import user_FeatureParams_dict


class FeatureParams_dict(TypedDict):
    root: root_FeatureParams_dict
    user: user_FeatureParams_dict

    user_filepath: str
    dev_mode: bool

    autostart: bool
    frames: dict[str, FrameParams_dict]
    state: dict
