from typing import Dict, List
from .Gtk_imports import GLib
from .frame_view import FrameView
from .parameters import FeatureParams


class FrameHandler:
    def __init__(self, feature_params: FeatureParams):
        self.feature_name = feature_params.name
        self.frames_params = feature_params.frames
        self.frames: Dict[str, FrameView] = {}

    def init(self, dev_mode: bool = False):
        for id, param in self.frames_params.items():
            self.frames[id] = FrameView(self.feature_name, id, param, dev_mode)

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
