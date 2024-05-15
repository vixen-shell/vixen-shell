from pydantic import BaseModel, ConfigDict
from typing import TypedDict
from .types import *

# ---------------------------------------------- - - -
# MODELS
#


class root_MarginParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    top: int | Disable | None = None
    right: int | Disable | None = None
    bottom: int | Disable | None = None
    left: int | Disable | None = None


class root_LayerFrameParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    monitor_id: int | Disable | None = None
    auto_exclusive_zone: bool | Disable | None = None
    exclusive_zone: int | Disable | None = None
    level: LevelKeys | Disable | None = None
    anchor_edge: AnchorEdgeKeys | Disable | None = None
    alignment: AlignmentKeys | Disable | None = None
    margins: root_MarginParams | Disable | None = None
    width: int | Disable | None = None
    height: int | Disable | None = None


class root_FrameParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    route: str
    show_on_startup: bool | Disable | None = None
    layer_frame: root_LayerFrameParams | Disable | None = None


class root_FeatureParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    autostart: bool | Disable | None = None
    frames: dict[str, root_FrameParams] | Disable | None = None
    templates: dict[str, root_FrameParams] | None = None
    state: dict | Disable | None = None


# ---------------------------------------------- - - -
# DICT
#


class root_MarginParams_dict(TypedDict):
    top: int | Disable
    right: int | Disable
    bottom: int | Disable
    left: int | Disable


class root_LayerFrameParams_dict(TypedDict):
    monitor_id: int | Disable
    auto_exclusive_zone: bool | Disable
    exclusive_zone: int | Disable
    level: LevelKeys | Disable
    anchor_edge: AnchorEdgeKeys | Disable
    alignment: AlignmentKeys | Disable
    margins: root_MarginParams_dict | Disable
    width: int | Disable
    height: int | Disable


class root_FrameParams_dict(TypedDict):
    name: str
    route: str
    show_on_startup: bool | Disable
    layer_frame: root_LayerFrameParams_dict | Disable


class root_FeatureParams_dict(TypedDict):
    autostart: bool | Disable
    frames: dict[str, root_FrameParams_dict] | Disable
    templates: dict[str, root_FrameParams_dict]
    state: dict | Disable
