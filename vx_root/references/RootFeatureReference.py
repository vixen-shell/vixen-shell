from typing import Literal, TypedDict, Callable
from .AbsFrames import AbsFrames
from .AbsParams import AbsParams
from .AbsLogger import AbsLogger

Disable = Literal["disable"]
LevelKeys = Literal["background", "bottom", "overlay", "top"]
AnchorEdgeKeys = Literal["top", "right", "bottom", "left", "full"]
AlignmentKeys = Literal["start", "center", "end", "stretch"]
FeatureContentType = Literal["action", "data", "file", "socket"]


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


class RootFeatureReference:
    @property
    def name(self) -> str: ...

    @property
    def frames(self) -> AbsFrames: ...

    @property
    def params(self) -> AbsParams: ...

    @property
    def logger(self) -> AbsLogger: ...

    def dialog(
        self,
        message: str,
        level: Literal["INFO", "WARNING"] = "INFO",
        title: str = "Vixen Shell",
    ) -> None: ...

    def init(self, value: root_FeatureParams_dict) -> None: ...
    def set_required_features(self, value: list[str]) -> None: ...

    def share(
        self, content_type: FeatureContentType
    ) -> Callable[[Callable], Callable]: ...

    def on_startup(self, callback: Callable[[], None]) -> Callable[[], None]: ...
    def on_shutdown(self, callback: Callable[[], None]) -> Callable[[], None]: ...
