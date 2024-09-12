from vx_features import ParamDataHandler
from .webview import webview
from .layerise_frame import layerise_frame, set_layer_frame
from ..Gtk_imports import GLib, Gtk, Gdk


def get_background_color(widget):
    context = widget.get_style_context()
    return context.get_background_color(Gtk.StateFlags.NORMAL)


def fade_in(window, current_opacity):
    current_opacity += 0.05
    window.set_opacity(current_opacity)
    if current_opacity < 1:
        GLib.timeout_add(30, fade_in, window, current_opacity)


class FrameView:
    def __init__(
        self,
        feature_name: str,
        frame_id: str,
        dev_mode: bool = False,
    ):
        self.is_first_render = True

        self.dev_mode = dev_mode
        self.feature_name: str = feature_name
        self.route: str = ParamDataHandler.get_value(
            f"{feature_name}.frames.{frame_id}.route"
        )

        def process():
            self.frame = Gtk.Window()

            self.frame.connect(
                "delete-event", lambda frame, event: (self.hide(), True)[1]
            )

            if ParamDataHandler.node_is_define(
                f"{feature_name}.frames.{frame_id}.layer_frame"
            ):
                self.webview = webview(
                    self.feature_name,
                    self.route,
                    self.dev_mode,
                    Gdk.RGBA(red=0, green=0, blue=0, alpha=0.0),
                )
                self.frame.add(self.webview)

                layerise_frame(
                    self.frame,
                    ParamDataHandler.get_value(
                        f"{feature_name}.frames.{frame_id}.name"
                    ),
                )
                set_layer_frame(self.frame, feature_name, frame_id)

                def on_layer_frame_params_changes(path, value):
                    def process():
                        set_layer_frame(self.frame, feature_name, frame_id)

                    GLib.idle_add(process)

                ParamDataHandler.add_param_listener(
                    f"{feature_name}.frames.{frame_id}.layer_frame",
                    on_layer_frame_params_changes,
                )

            else:
                self.webview = webview(
                    self.feature_name,
                    self.route,
                    self.dev_mode,
                    get_background_color(self.frame),
                )
                self.frame.add(self.webview)

                self.frame.set_title(
                    ParamDataHandler.get_value(f"{feature_name}.frames.{frame_id}.name")
                )

            self.frame.realize()

        GLib.idle_add(process)

        if ParamDataHandler.get_value(
            f"{feature_name}.frames.{frame_id}.show_on_startup"
        ):
            self.show()

    @property
    def is_visible(self) -> bool:
        return self.frame.get_visible()

    def show(self):
        def process():
            if not self.is_visible:
                if self.is_first_render:
                    self.is_first_render = False
                    fade_in(self.frame, 0)

                self.frame.show_all()

        GLib.idle_add(process)

    def hide(self):
        def process():
            if self.is_visible:
                self.frame.hide()

        GLib.idle_add(process)
