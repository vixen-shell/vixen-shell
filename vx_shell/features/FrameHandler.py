from vx_features import ParamDataHandler
from typing import Dict, List
from .frame_view import FrameView


class FrameHandler:
    def __init__(self, feature_name: str):
        self.feature_name = feature_name
        self.frames: Dict[str, FrameView] = {}

    def init(self, dev_mode: bool = False):
        frame_ids = ParamDataHandler.get_frame_ids(self.feature_name)

        if frame_ids:
            for id in frame_ids:
                self.frames[id] = FrameView(self.feature_name, id, dev_mode)

    def open(self, id: str):
        self.frames[id].show()

    def close(self, id: str):
        self.frames[id].hide()

    def cleanup(self):
        for frame in self.frames.values():
            frame.hide()

        self.frames = {}

    @property
    def frame_ids(self) -> List[str]:
        return list(self.frames.keys())

    @property
    def active_frame_ids(self) -> List[str]:
        return [id for id, frame in self.frames.items() if frame.is_visible]
