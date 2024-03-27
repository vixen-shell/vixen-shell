from typing import Optional, Dict, TypedDict
from pydantic import BaseModel
from .types import *

# ---------------------------------------------- - - -
# MODELS


class RootMarginParams(BaseModel):
    top: Optional[int | Disable] = None
    right: Optional[int | Disable] = None
    bottom: Optional[int | Disable] = None
    left: Optional[int | Disable] = None


class RootLayerFrameParams(BaseModel):
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
    name: str
    route: str
    show_on_startup: Optional[bool | Disable] = None
    layer_frame: Optional[RootLayerFrameParams | Disable] = None
    multi_frame: Optional[bool | Disable] = None


class RootFeatureParams(BaseModel):
    name: str
    frames: Dict[str, RootFrameParams]
    state: Optional[Dict[str, None | str | int | float | bool] | Disable] = None
