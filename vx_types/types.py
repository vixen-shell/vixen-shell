from typing import Literal, Callable, Union

LifeCycleCleanUpHandler = Callable[[], None]
LifeCycleHandler = Callable[[], Union[LifeCycleCleanUpHandler | Literal[False] | None]]

Disable = Literal["disable"]
LevelKeys = Literal["background", "bottom", "overlay", "top"]
AnchorEdgeKeys = Literal["top", "right", "bottom", "left", "full"]
AlignmentKeys = Literal["start", "center", "end", "stretch"]

ParamPermission = Literal["DISABLED", "ROOT", "RESTRICTED", "USER"]

FeatureContentType = Literal["task", "data", "socket", "menu"]
