from vx_types import LifeCycleCleanUpHandler
from .webview import webview
from .Frame import Frame
from ..Gtk_imports import WebKit2


class WindowFrame(Frame):
    def __init__(self, feature_name: str, frame_id: str, dev_mode: bool):
        super().__init__(feature_name, frame_id, dev_mode)
        self.init_content()
        self.realize()

    def init_content(self):
        web_view = webview(
            feature_name=self.feature_name,
            route=self.params("route"),
            frame_id=self.frame_id,
            dev_mode=self.dev_mode,
        )
        web_view.connect("button-press-event", self.on_button_press_event)
        web_view.connect("load_changed", self.on_load_changed)
        self.add(web_view)

    def on_load_changed(self, webview, load_event):
        if load_event == WebKit2.LoadEvent.FINISHED and not self.is_visible():
            self.show_all()


def create_window_frame(
    feature_name: str,
    frame_id: str,
    dev_mode: bool,
    cleanup_handler: LifeCycleCleanUpHandler,
):
    frame = WindowFrame(feature_name, frame_id, dev_mode)

    if callable(cleanup_handler):
        frame.cleanup_handler = cleanup_handler

    return frame
