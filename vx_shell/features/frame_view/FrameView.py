from vx_features import ParamDataHandler
from vx_systray import SysTrayState
from vx_gtk import GLib, Gtk, Gdk, WebKit2
from vx_types import LifeCycleHandler, LifeCycleCleanUpHandler
from vx_logger import Logger
from typing import Literal
from .webview import webview, get_uri
from .layerise_frame import layerise_frame, set_layer_frame


class FrameView:
    def __init__(
        self,
        feature_name: str,
        frame_id: str,
        dev_mode: bool = False,
    ):
        self.frame: Gtk.Window = None
        self.webview: WebKit2.WebView = None

        self.feature_name = feature_name
        self.frame_id = frame_id
        self.route: str = ParamDataHandler.get_value(
            f"{feature_name}.frames.{frame_id}.route"
        )
        self.dev_mode = dev_mode

        self.startup_handler: LifeCycleHandler = ParamDataHandler.get_value(
            f"{feature_name}.frames.{frame_id}.life_cycle"
        )
        self.cleanup_handler: LifeCycleCleanUpHandler = None

        self.last_button_press_event: Gdk.EventButton = None

        if ParamDataHandler.get_value(
            f"{feature_name}.frames.{frame_id}.show_on_startup"
        ):
            self.show()

    @property
    def is_visible(self) -> bool:
        return self.frame and self.frame.get_visible()

    def handle_lifecycle(self, event: Literal["startup", "cleanup"]) -> bool:
        if event == "startup" and self.startup_handler:
            startup = True

            try:
                cleanup_handler = self.startup_handler()

                if callable(cleanup_handler):
                    self.cleanup_handler = cleanup_handler
                elif cleanup_handler == False:
                    Logger.log(
                        f"[{self.feature_name}]: frame ({self.frame_id}) startup sequence return 'False'",
                        "WARNING",
                    )
                    startup = False

            except Exception as exception:
                Logger.log_exception(exception)
                startup = False

            return startup

        if event == "cleanup" and self.cleanup_handler:
            try:
                self.cleanup_handler()
            except Exception as exception:
                Logger.log_exception(exception)

        return True

    def show(self):
        show_frame(self)

    def hide(self):
        hide_frame(self)

    def popup_context_menu(self, menu: Gtk.Menu):
        def process():
            menu.popup_at_pointer(self.last_button_press_event)

        GLib.idle_add(process)

    def popup_dbus_menu(self, service_name: str):
        def process():
            if service_name in SysTrayState.menus:
                SysTrayState.menus[service_name].popup_at_pointer(
                    self.last_button_press_event
                )

        GLib.idle_add(process)


def get_background_color(widget):
    context = widget.get_style_context()
    return context.get_background_color(Gtk.StateFlags.NORMAL)


def set_webview(frame_view: FrameView, layer: bool = False):
    background_color = (
        Gdk.RGBA(0, 0, 0, 0) if layer else get_background_color(frame_view.frame)
    )

    if layer:
        screen = frame_view.frame.get_screen()
        rgba_visual = screen.get_rgba_visual()
        if rgba_visual is not None:
            frame_view.frame.set_visual(rgba_visual)

        frame_view.frame.set_app_paintable(True)

    frame_view.webview = webview(
        frame_view.feature_name,
        frame_view.route,
        frame_view.frame_id,
        frame_view.dev_mode,
        background_color,
    )

    frame_view.frame.add(frame_view.webview)


def show_frame(frame_view: FrameView):
    def create_frame():
        frame_view.frame = Gtk.Window()

        if ParamDataHandler.node_is_define(
            f"{frame_view.feature_name}.frames.{frame_view.frame_id}.layer_frame"
        ):
            set_webview(frame_view, True)

            layerise_frame(frame_view.frame, "vx_layer")
            set_layer_frame(
                frame_view.frame, frame_view.feature_name, frame_view.frame_id
            )

            def on_layer_frame_params_changes(path, value):
                def process():
                    set_layer_frame(
                        frame_view.frame,
                        frame_view.feature_name,
                        frame_view.frame_id,
                    )

                GLib.idle_add(process)

            ParamDataHandler.add_param_listener(
                f"{frame_view.feature_name}.frames.{frame_view.frame_id}.layer_frame",
                on_layer_frame_params_changes,
            )

        else:
            set_webview(frame_view)

            frame_view.frame.set_title(
                ParamDataHandler.get_value(
                    f"{frame_view.feature_name}.frames.{frame_view.frame_id}.name"
                )
            )

        def on_button_press_event(widget, event: Gdk.EventButton):
            frame_view.last_button_press_event = event.copy()
            return False

        def on_delete_event(widget, event):
            frame_view.hide()
            return True

        frame_view.webview.connect("button-press-event", on_button_press_event)
        frame_view.frame.connect("delete-event", on_delete_event)
        frame_view.webview.show()
        frame_view.frame.hide()

    def show():
        if not frame_view.is_visible:
            startup = frame_view.handle_lifecycle("startup")

            if startup:
                try:
                    if not frame_view.frame:
                        create_frame()
                    else:
                        frame_view.webview.load_uri(
                            get_uri(
                                frame_view.feature_name,
                                frame_view.route,
                                frame_view.frame_id,
                                frame_view.dev_mode,
                            )
                        )

                    GLib.timeout_add(200, frame_view.frame.show)
                except:
                    frame_view.handle_lifecycle("cleanup")

    GLib.idle_add(show)


def hide_frame(frame_view: FrameView):
    def hide():
        if frame_view.is_visible:
            frame_view.frame.hide()
            frame_view.webview.load_html("")
            frame_view.handle_lifecycle("cleanup")

    GLib.idle_add(hide)
