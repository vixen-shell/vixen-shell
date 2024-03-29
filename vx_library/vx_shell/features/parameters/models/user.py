from typing import Optional, Dict, TypedDict
from pydantic import BaseModel, validator
from .types import *

# ---------------------------------------------- - - -
# MODELS


class UserMarginParams(BaseModel):
    top: Optional[int] = None
    right: Optional[int] = None
    bottom: Optional[int] = None
    left: Optional[int] = None


class UserLayerFrameParams(BaseModel):
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
    show_on_startup: Optional[bool] = None
    layer_frame: Optional[UserLayerFrameParams] = None


class UserFeatureParams(BaseModel):
    frames: Optional[Dict[str, UserFrameParams]] = None
    state: Optional[Dict[str, None | str | int | float | bool]] = None
