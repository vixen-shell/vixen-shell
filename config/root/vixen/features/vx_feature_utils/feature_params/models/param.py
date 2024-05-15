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


class FrameParams_dict(TypedDict):
    name: str
    route: str
    show_on_startup: bool
    layer_frame: LayerFrameParams_dict


class FeatureParams_dict(TypedDict):
    user_filepath: str
    dev_mode: bool

    autostart: bool
    frames: dict[str, FrameParams_dict]
    state: dict
