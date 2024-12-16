from vx_types import LifeCycleCleanUpHandler
from vx_systray import SysTrayState
from .frame_utils import FrameParams, handle_frame_startup, handle_frame_cleanup
from ..Gtk_imports import Gtk, Gdk, GLib


class Frame(Gtk.Window):
    def __init__(self, feature_name: str, frame_id: str, dev_mode: bool):
        super().__init__()

        self.params: FrameParams = FrameParams(feature_name, frame_id)
        self.feature_name: str = feature_name
        self.frame_id: str = frame_id
        self.dev_mode: bool = dev_mode

        self.cleanup_handler: LifeCycleCleanUpHandler = None
        self.last_button_press_event: Gdk.EventButton = None

        self.connect("destroy", lambda w: handle_frame_cleanup(self.cleanup_handler))

    def on_button_press_event(self, widget: Gtk.Widget, event: Gdk.EventButton):
        self.last_button_press_event = event.copy()
        return False

    def popup_context_menu(self, menu: Gtk.Menu):
        def process():
            if self.last_button_press_event:
                menu.popup_at_pointer(self.last_button_press_event)

        GLib.idle_add(process)

    def popup_dbus_menu(self, service_name: str):
        def process():
            if self.last_button_press_event and service_name in SysTrayState.menus:
                SysTrayState.menus[service_name].popup_at_pointer(
                    self.last_button_press_event
                )

        GLib.idle_add(process)


def create_frame(
    app: Gtk.Application, feature_name: str, frame_id: str, dev_mode: bool
):
    cleanup_handler = handle_frame_startup(feature_name, frame_id)

    if not cleanup_handler == False:
        frame_params = FrameParams(feature_name, frame_id)

        if frame_params.node_is_define("layer_frame"):
            from .LayerFrame import create_layer_frame

            return create_layer_frame(
                app, feature_name, frame_id, dev_mode, cleanup_handler
            )
        else:
            from .WindowFrame import create_window_frame

            return create_window_frame(
                app, feature_name, frame_id, dev_mode, cleanup_handler
            )
