from typing import Dict, Callable
from threading import Event as ThreadEvent
from vx_features import ParamDataHandler
from vx_types import user_FrameParams_dict
from .frame_handler_utils import FeatureFrameParams
from ..Frame import Frame, create_frame
from ..Gtk_imports import Gtk, GLib


class FeatureFrameHandler:
    def __init__(self, feature_name: str, dev_mode: bool):
        self.dev_mode = dev_mode
        self.feature_name = feature_name
        self.frames: Dict[str, Frame] = {}
        self.frame_params = FeatureFrameParams(feature_name)

        for frame_id in self.frame_ids:
            if self.frame_params(frame_id, "show_on_startup"):
                self.open(frame_id)

    def cleanup(self):
        cleanup_is_done = ThreadEvent()

        def process():
            active_frame_ids = list(self.frames.keys())

            for frame_id in active_frame_ids:
                self.frames[frame_id].destroy()

            cleanup_is_done.set()

        GLib.idle_add(process)
        cleanup_is_done.wait()

    @property
    def frame_ids(self):
        return self.frame_params.frame_ids

    @property
    def active_frame_ids(self):
        return list(self.frames.keys())

    def exists(self, frame_id: str):
        return frame_id in self.frame_ids

    def is_open(self, frame_id: str):
        return frame_id in self.active_frame_ids

    def open(self, frame_id: str, after_open: Callable[[list[str]], None] = None):
        def init():
            if self.exists(frame_id) and not self.is_open(frame_id):
                frame = create_frame(self.feature_name, frame_id, self.dev_mode)
                frame.connect("destroy", lambda w: self.frames.pop(frame_id))
                self.frames[frame_id] = frame

                if after_open:
                    after_open(self.active_frame_ids)

        GLib.idle_add(init)

    def close(self, frame_id: str, after_close: Callable[[list[str]], None] = None):
        def process():
            if self.exists(frame_id) and self.is_open(frame_id):
                self.frames[frame_id].destroy()

                if after_close:
                    after_close(self.active_frame_ids)

        GLib.idle_add(process)

    def new_frame_from_template(
        self, frame_id: str, frame_params_dict: user_FrameParams_dict
    ) -> bool:
        if self.exists(frame_id):
            return

        result = ParamDataHandler.new_frame_from_template(
            self.feature_name, frame_id, frame_params_dict
        )

        if result:
            if self.frame_params(frame_id, "show_on_startup"):
                self.open(frame_id)

        return result

    def remove_frame_from_template(self, frame_id: str) -> bool:
        if not self.exists(frame_id):
            return

        result = ParamDataHandler.remove_frame_from_template(
            self.feature_name, frame_id
        )

        if result and self.is_open(frame_id):
            self.close_frame(frame_id)

        return result

    def popup_context_menu(self, frame_id: str, menu: Gtk.Menu):
        if not self.exists(frame_id) or not self.is_open(frame_id):
            return

        self.frames[frame_id].popup_context_menu(menu)

    def popup_dbus_menu(self, frame_id: str, service_name: str):
        if not self.exists(frame_id) or not self.is_open(frame_id):
            return

        self.frames[frame_id].popup_dbus_menu(service_name)


class FrameHandler:
    __frames: dict[str, FeatureFrameHandler] = {}

    @staticmethod
    def init_feature(feature_name: str, dev_mode: bool):
        FrameHandler.__frames[feature_name] = FeatureFrameHandler(
            feature_name, dev_mode
        )

    @staticmethod
    def cleanup(feature_name: str):
        return FrameHandler.__frames[feature_name].cleanup()

    @staticmethod
    def frame_ids(feature_name: str):
        return FrameHandler.__frames[feature_name].frame_ids

    @staticmethod
    def active_frame_ids(feature_name: str):
        return FrameHandler.__frames[feature_name].active_frame_ids

    @staticmethod
    def open(
        feature_name: str, frame_id: str, after_open: Callable[[list[str]], None] = None
    ):
        return FrameHandler.__frames[feature_name].open(frame_id, after_open)

    @staticmethod
    def close(
        feature_name: str,
        frame_id: str,
        after_close: Callable[[list[str]], None] = None,
    ):
        return FrameHandler.__frames[feature_name].close(frame_id, after_close)

    @staticmethod
    def new_frame_from_template(
        feature_name: str, frame_id: str, frame_params_dict: user_FrameParams_dict
    ) -> bool:
        return FrameHandler.__frames[feature_name].new_frame_from_template(
            frame_id, frame_params_dict
        )

    @staticmethod
    def remove_frame_from_template(feature_name: str, frame_id: str) -> bool:
        return FrameHandler.__frames[feature_name].remove_frame_from_template(frame_id)

    @staticmethod
    def popup_context_menu(feature_name: str, frame_id: str, menu: Gtk.Menu):
        return FrameHandler.__frames[feature_name].popup_context_menu(frame_id, menu)

    @staticmethod
    def popup_dbus_menu(feature_name: str, frame_id: str, service_name: str):
        return FrameHandler.__frames[feature_name].popup_dbus_menu(
            frame_id, service_name
        )
