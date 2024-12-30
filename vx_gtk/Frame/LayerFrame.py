from vx_types import LifeCycleCleanUpHandler
from .frame_utils import set_frame_as_transparent
from .webview import webview
from .Frame import Frame
from .layerise_frame import layerise_frame, set_layer_frame
from ..Gtk_imports import GLib, WebKit2


class LayerFrame(Frame):
    def __init__(self, feature_name: str, frame_id: str, dev_mode: bool):
        super().__init__(feature_name, frame_id, dev_mode)
        self.init_content()
        self.layerise()
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
        web_view.show()

        self.add(web_view)

    def layerise(self):
        set_frame_as_transparent(self)
        layerise_frame(self)
        set_layer_frame(self)

        def on_layer_frame_params_changes(path: str, value):
            GLib.idle_add(lambda: set_layer_frame(self))

        self.params.add_listener("layer_frame", on_layer_frame_params_changes)

        self.connect(
            "destroy",
            lambda w: self.params.remove_listener(
                "layer_frame", on_layer_frame_params_changes
            ),
        )

    def on_load_changed(self, webview, load_event):
        if load_event == WebKit2.LoadEvent.FINISHED and not self.is_visible():
            self.connect("show", self.fade_in)
            self.set_opacity(0)
            self.show()

    def fade_in(self, *args):
        def increase_opacity():
            current_opacity = self.get_opacity()
            if current_opacity < 1.0:
                self.set_opacity(current_opacity + 0.05)
                return True
            return False

        GLib.timeout_add(25, increase_opacity)


def create_layer_frame(
    feature_name: str,
    frame_id: str,
    dev_mode: bool,
    cleanup_handler: LifeCycleCleanUpHandler,
):
    frame = LayerFrame(feature_name, frame_id, dev_mode)

    if callable(cleanup_handler):
        frame.cleanup_handler = cleanup_handler

    return frame
