from pydantic import BaseModel, ConfigDict, root_validator
from typing import Any, TypedDict
from .types import *

# ---------------------------------------------- - - -
# MODELS
#


class root_MarginParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    top: int | list[int] | Disable | None = None
    right: int | list[int] | Disable | None = None
    bottom: int | list[int] | Disable | None = None
    left: int | list[int] | Disable | None = None


class root_LayerFrameParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    monitor_id: int | list[int] | Disable | None = None
    auto_exclusive_zone: bool | Disable | None = None
    exclusive_zone: int | list[int] | Disable | None = None
    level: LevelKeys | list[LevelKeys] | Disable | None = None
    anchor_edge: AnchorEdgeKeys | list[AnchorEdgeKeys] | Disable | None = None
    alignment: AlignmentKeys | list[AlignmentKeys] | Disable | None = None
    margins: root_MarginParams | Disable | None = None
    width: int | list[int] | Disable | None = None
    height: int | list[int] | Disable | None = None


class root_FrameParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    route: str
    show_on_startup: bool | Disable | None = None
    layer_frame: root_LayerFrameParams | Disable | None = None


class root_FeatureParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    autostart: bool | Disable | None = None
    frames: dict[str, root_FrameParams] | Disable = "disable"
    templates: dict[str, root_FrameParams] | None = None
    state: Disable | None = None

    def model_post_init(self, __context: Any) -> None:
        if self.frames == "disable":
            if self.templates is not None:
                raise ValueError(
                    "The 'frames' field is disabled. The 'templates' field should not be defined"
                )


# ---------------------------------------------- - - -
# DICT
#


class root_MarginParams_dict(TypedDict):
    top: int | list[int] | Disable
    right: int | list[int] | Disable
    bottom: int | list[int] | Disable
    left: int | list[int] | Disable


class root_LayerFrameParams_dict(TypedDict):
    monitor_id: int | list[int] | Disable
    auto_exclusive_zone: bool | Disable
    exclusive_zone: int | list[int] | Disable
    level: LevelKeys | list[LevelKeys] | Disable
    anchor_edge: AnchorEdgeKeys | list[AnchorEdgeKeys] | Disable
    alignment: AlignmentKeys | list[AlignmentKeys] | Disable
    margins: root_MarginParams_dict | Disable
    width: int | list[int] | Disable
    height: int | list[int] | Disable


class root_FrameParams_dict(TypedDict):
    name: str
    route: str
    show_on_startup: bool | Disable
    layer_frame: root_LayerFrameParams_dict | Disable


class root_FeatureParams_dict(TypedDict):
    autostart: bool | Disable
    frames: dict[str, root_FrameParams_dict] | Disable
    templates: dict[str, root_FrameParams_dict]
    state: Disable
