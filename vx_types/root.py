from pydantic import BaseModel, ConfigDict
from typing import Any, TypedDict, Union
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
    transparent: bool = True


class root_FrameParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    route: str
    show_on_startup: bool | Disable | None = None
    layer_frame: root_LayerFrameParams | Disable | None = None
    life_cycle: LifeCycleHandler | Disable = "disable"


class root_FeatureParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | Disable = "disable"
    autostart: bool | Disable | None = None
    frames: dict[str, root_FrameParams] | Disable = "disable"
    templates: dict[str, root_FrameParams] | None = None
    life_cycle: LifeCycleHandler | Disable = "disable"
    wait_startup: tuple[str] | Disable = "disable"
    state: dict | None = {}

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
    top: Union[int | list[int] | Disable]
    right: Union[int | list[int] | Disable]
    bottom: Union[int | list[int] | Disable]
    left: Union[int | list[int] | Disable]


class root_LayerFrameParams_dict(TypedDict):
    monitor_id: Union[int | list[int] | Disable]
    auto_exclusive_zone: Union[bool | Disable]
    exclusive_zone: Union[int | list[int] | Disable]
    level: Union[LevelKeys | list[LevelKeys] | Disable]
    anchor_edge: Union[AnchorEdgeKeys | list[AnchorEdgeKeys] | Disable]
    alignment: Union[AlignmentKeys | list[AlignmentKeys] | Disable]
    margins: Union[root_MarginParams_dict | Disable]
    width: Union[int | list[int] | Disable]
    height: Union[int | list[int] | Disable]
    transparent: bool


class root_FrameParams_dict(TypedDict):
    name: str
    route: str
    show_on_startup: Union[bool | Disable]
    layer_frame: Union[root_LayerFrameParams_dict | Disable]
    life_cycle: LifeCycleHandler


class root_FeatureParams_dict(TypedDict):
    title: str
    autostart: Union[bool | Disable]
    frames: Union[dict[str, root_FrameParams_dict] | Disable]
    templates: dict[str, root_FrameParams_dict]
    life_cycle: LifeCycleHandler
    wait_startup: tuple[str]
    state: dict
