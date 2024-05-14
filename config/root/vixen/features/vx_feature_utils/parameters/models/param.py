from typing import Optional, Dict, TypedDict
from pydantic import BaseModel, ConfigDict
from .types import *

# ---------------------------------------------- - - -
# MODELS


class MarginParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    top: Optional[int] = None
    right: Optional[int] = None
    bottom: Optional[int] = None
    left: Optional[int] = None


class LayerFrameParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    monitor_id: Optional[int] = None
    auto_exclusive_zone: Optional[bool] = None
    exclusive_zone: Optional[int] = None
    level: Optional[LevelKeys] = None
    anchor_edge: Optional[AnchorEdgeKeys] = None
    alignment: Optional[AlignmentKeys] = None
    margins: Optional[MarginParams] = None
    width: Optional[int] = None
    height: Optional[int] = None


class FrameParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    route: str
    template: Optional[str] = None
    show_on_startup: Optional[bool] = None
    layer_frame: Optional[LayerFrameParams] = None


# ---------------------------------------------- - - -
# DICT


class MarginParamsDict(TypedDict):
    top: Optional[int]
    right: Optional[int]
    bottom: Optional[int]
    left: Optional[int]


class LayerFrameParamsDict(TypedDict):
    monitor_id: Optional[int]
    auto_exclusive_zone: Optional[bool]
    exclusive_zone: Optional[int]
    level: Optional[LevelKeys]
    anchor_edge: Optional[AnchorEdgeKeys]
    alignment: Optional[AlignmentKeys]
    margins: Optional[MarginParamsDict]
    width: Optional[int]
    height: Optional[int]


class FrameParamsDict(TypedDict):
    name: str
    route: str
    template: Optional[str]
    show_on_startup: Optional[bool]
    layer_frame: Optional[LayerFrameParamsDict]


class FeatureParamsDict(TypedDict):
    path: str
    frames: Optional[Dict[str, FrameParamsDict]]
    state: Optional[Dict[str, None | str | int | float | bool]]
    start: Optional[bool]
