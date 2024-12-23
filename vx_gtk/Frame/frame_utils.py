from vx_types import LifeCycleHandler, LifeCycleCleanUpHandler
from vx_features import ParamDataHandler
from vx_logger import Logger
from typing import Callable, Any
from ..Gtk_imports import Gtk, Gdk


def handle_frame_startup(feature_name: str, frame_id: str):
    startup_handler: LifeCycleHandler = ParamDataHandler.get_value(
        f"{feature_name}.frames.{frame_id}.life_cycle"
    )

    if startup_handler is None:
        return

    if not callable(startup_handler):
        return False

    try:
        cleanup_handler = startup_handler()

        if cleanup_handler == False:
            return False

    except Exception as e:
        Logger.log_exception(e)
        return False

    return cleanup_handler


def handle_frame_cleanup(cleanup_handler: LifeCycleCleanUpHandler | None):
    if cleanup_handler:
        try:
            cleanup_handler()
        except Exception as exception:
            Logger.log_exception(exception)


class FrameParams:
    def __init__(self, feature_name: str, frame_id: str):
        self.__main_path = f"{feature_name}.frames.{frame_id}"

    def __call__(self, path: str):
        return ParamDataHandler.get_value(f"{self.__main_path}.{path}")

    def node_is_define(self, path: str):
        return ParamDataHandler.node_is_define(f"{self.__main_path}.{path}")

    def add_listener(self, path: str, listener: Callable[[str, Any], None]):
        return ParamDataHandler.add_param_listener(
            f"{self.__main_path}.{path}", listener
        )

    def remove_listener(self, path: str, listener: Callable[[str, Any], None]):
        return ParamDataHandler.remove_param_listener(
            f"{self.__main_path}.{path}", listener
        )


def set_frame_as_transparent(frame: Gtk.Window):
    screen = frame.get_screen()
    rgba_visual = screen.get_rgba_visual()

    if rgba_visual:
        frame.set_visual(rgba_visual)
        frame.set_app_paintable(True)
