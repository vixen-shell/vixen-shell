from typing import Optional, Dict, TypedDict
from pydantic import BaseModel, ConfigDict
from .types import *

# ---------------------------------------------- - - -
# MODELS


class RootMarginParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    top: Optional[int | Disable] = None
    right: Optional[int | Disable] = None
    bottom: Optional[int | Disable] = None
    left: Optional[int | Disable] = None


class RootLayerFrameParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    monitor_id: Optional[int | Disable] = None
    auto_exclusive_zone: Optional[bool | Disable] = None
    exclusive_zone: Optional[int | Disable] = None
    level: Optional[LevelKeys | Disable] = None
    anchor_edge: Optional[AnchorEdgeKeys | Disable] = None
    alignment: Optional[AlignmentKeys | Disable] = None
    margins: Optional[RootMarginParams | Disable] = None
    width: Optional[int | Disable] = None
    height: Optional[int | Disable] = None


class RootFrameParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    route: str
    show_on_startup: Optional[bool | Disable] = None
    layer_frame: Optional[RootLayerFrameParams | Disable] = None


class RootFeatureParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frames: Dict[str, RootFrameParams]
    templates: Optional[Dict[str, RootFrameParams]] = None
    state: Optional[Dict[str, None | str | int | float | bool] | Disable] = None
    start: Optional[bool | Disable] = None


# ---------------------------------------------- - - -
# DICT


class RootMarginParamsDict(TypedDict):
    top: Optional[int | Disable]
    right: Optional[int | Disable]
    bottom: Optional[int | Disable]
    left: Optional[int | Disable]


class RootLayerFrameParamsDict(TypedDict):
    monitor_id: Optional[int | Disable]
    auto_exclusive_zone: Optional[bool | Disable]
    exclusive_zone: Optional[int | Disable]
    level: Optional[LevelKeys | Disable]
    anchor_edge: Optional[AnchorEdgeKeys | Disable]
    alignment: Optional[AlignmentKeys | Disable]
    margins: Optional[RootMarginParamsDict | Disable]
    width: Optional[int | Disable]
    height: Optional[int | Disable]


class RootFrameParamsDict(TypedDict):
    name: str
    route: str
    show_on_startup: Optional[bool | Disable]
    layer_frame: Optional[RootLayerFrameParamsDict | Disable]


class RootFeatureParamsDict(TypedDict):
    frames: Dict[str, RootFrameParamsDict]
    templates: Optional[Dict[str, RootFrameParamsDict]]
    state: Optional[Dict[str, None | str | int | float | bool] | Disable]
    start: Optional[bool | Disable]
