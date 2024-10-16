from vx_features import ParamDataHandler
from vx_root.root_utils.classes import ContextMenu
from vx_systray import SysTrayState
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
        self.last_webview_press_event = None

        def on_webview_press_event(widget, event):
            self.last_webview_press_event = event.copy()
            return False

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
                    frame_id,
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
                    frame_id,
                    self.dev_mode,
                    get_background_color(self.frame),
                )
                self.frame.add(self.webview)

                self.frame.set_title(
                    ParamDataHandler.get_value(f"{feature_name}.frames.{frame_id}.name")
                )

            self.webview.connect("button-press-event", on_webview_press_event)
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

    def popup_context_menu(self, context_menu: ContextMenu):
        def process():
            context_menu.menu.popup_at_pointer(self.last_webview_press_event)

        GLib.idle_add(process)

    def popup_dbus_menu(self, service_name: str):
        def process():
            if service_name in SysTrayState.menus:
                SysTrayState.menus[service_name].popup_at_pointer(
                    self.last_webview_press_event
                )

        GLib.idle_add(process)

    def set_zoom_level(self, factor: float):
        def process():
            self.webview.set_zoom_level(factor)

        GLib.idle_add(process)
