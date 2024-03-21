import json
from typing import Literal, Optional, Dict
from pydantic import BaseModel, validator


def read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: str, data: dict):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


LevelKeys = Literal["background", "bottom", "overlay", "top"]
AnchorEdgeKeys = Literal["top", "right", "bottom", "left", "full"]
AlignmentKeys = Literal["start", "center", "end", "stretch"]


class MarginParams(BaseModel):
    top: Optional[int] = None
    right: Optional[int] = None
    bottom: Optional[int] = None
    left: Optional[int] = None


class LayerFrameParams(BaseModel):
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
    name: str
    route: str
    show_on_startup: Optional[bool] = None
    layer_frame: Optional[LayerFrameParams] = None
    multi_frame: Optional[bool] = None

    @validator("multi_frame", pre=True)
    def validate_multi_frame(cls, v, values):
        if values.get("layer_frame") is not None and v is not None:
            raise ValueError("A layer frame cannot be a multi frame")
        return v


class FeatureParams(BaseModel):
    path: str
    name: str
    frames: Dict[str, FrameParams]
    state: Optional[Dict[str, None | str | int | float | bool]] = None

    @staticmethod
    def create(path: str):
        data: Dict = read_json(path)
        data["path"] = path

        return FeatureParams(**data)

    def save(self):
        write_json(self.path, self.model_dump(exclude={"path"}, exclude_none=True))

    @property
    def single_frames(self) -> Dict[str, FrameParams]:
        return {
            key: frame for key, frame in self.frames.items() if not frame.multi_frame
        }

    @property
    def multi_frames(self) -> Dict[str, FrameParams]:
        return {key: frame for key, frame in self.frames.items() if frame.multi_frame}
