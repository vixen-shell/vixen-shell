from typing import Optional, Dict, TypedDict
from pydantic import BaseModel, ConfigDict
from .types import *

# ---------------------------------------------- - - -
# MODELS


class UserMarginParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    top: Optional[int] = None
    right: Optional[int] = None
    bottom: Optional[int] = None
    left: Optional[int] = None


class UserLayerFrameParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    monitor_id: Optional[int] = None
    auto_exclusive_zone: Optional[bool] = None
    exclusive_zone: Optional[int] = None
    level: Optional[LevelKeys] = None
    anchor_edge: Optional[AnchorEdgeKeys] = None
    alignment: Optional[AlignmentKeys] = None
    margins: Optional[UserMarginParams] = None
    width: Optional[int] = None
    height: Optional[int] = None


class UserFrameParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    template: Optional[str] = None
    show_on_startup: Optional[bool] = None
    layer_frame: Optional[UserLayerFrameParams] = None


class UserFeatureParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frames: Optional[Dict[str, UserFrameParams]] = None
    state: Optional[Dict[str, None | str | int | float | bool]] = None
    start: Optional[bool] = None


# ---------------------------------------------- - - -
# MODELS


class UserMarginParamsDict(TypedDict):
    top: Optional[int]
    right: Optional[int]
    bottom: Optional[int]
    left: Optional[int]


class UserLayerFrameParamsDict(TypedDict):
    monitor_id: Optional[int]
    auto_exclusive_zone: Optional[bool]
    exclusive_zone: Optional[int]
    level: Optional[LevelKeys]
    anchor_edge: Optional[AnchorEdgeKeys]
    alignment: Optional[AlignmentKeys]
    margins: Optional[UserMarginParamsDict]
    width: Optional[int]
    height: Optional[int]


class UserFrameParamsDict(TypedDict):
    template: Optional[str]
    show_on_startup: Optional[bool]
    layer_frame: Optional[UserLayerFrameParamsDict]


class UserFeatureParamsDict(TypedDict):
    frames: Optional[Dict[str, UserFrameParamsDict]]
    state: Optional[Dict[str, None | str | int | float | bool]]
    start: Optional[bool]
