from vx_features import ParamDataHandler
from vx_gtk import Gtk
from typing import Dict, List
from vx_types import user_FrameParams_dict
from .frame_view import FrameView


class FrameHandler:

    def __init__(self, feature_name: str, dev_mode: bool = False):
        self.feature_name = feature_name
        self.frames: Dict[str, FrameView] = {}
        self.dev_mode = dev_mode

    def init(self):
        root_frame_ids = ParamDataHandler.get_frame_ids(self.feature_name)

        if root_frame_ids:
            for id in root_frame_ids:
                if not id in self.frames:
                    self.frames[id] = FrameView(self.feature_name, id, self.dev_mode)

    def open(self, id: str):
        self.frames[id].show()

    def close(self, id: str):
        self.frames[id].hide()

    def popup_context_menu(self, frame_id: str, menu: Gtk.Menu):
        self.frames[frame_id].popup_context_menu(menu)

    def popup_dbus_menu(self, frame_id: str, service_name: str):
        self.frames[frame_id].popup_dbus_menu(service_name)

    def new_frame_from_template(
        self, frame_id: str, frame_params_dict: user_FrameParams_dict
    ) -> bool:
        if ParamDataHandler.new_frame_from_template(
            self.feature_name, frame_id, frame_params_dict
        ):
            # self.init()
            return True

        return False

    def remove_frame_from_template(self, frame_id: str) -> bool:
        if ParamDataHandler.remove_frame_from_template(self.feature_name, frame_id):
            self.frames[frame_id].hide()
            self.frames.pop(frame_id)
            return True

        return False

    def cleanup(self):
        for frame in self.frames.values():
            frame.hide()

        self.frames = {}

    @property
    def frame_ids(self) -> List[str]:
        return list(self.frames.keys())

    @property
    def active_frame_ids(self) -> List[str]:
        return [id for id, frame in self.frames.items() if frame.is_open]
