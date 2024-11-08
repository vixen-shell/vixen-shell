from vx_gtk import Gdk, Gtk, WebKit2, GLib
from vx_systray import SysTrayState
from .webview import webview, get_uri
from ..layerise import layerise_window, set_layer, Levels


class PopupFrame:
    def __init__(self):
        self.frame: Gtk.Window = None
        self.webview: WebKit2.WebView = None
        self.last_button_press_event: Gdk.EventButton = None
        self.feature_name: str = None

    @property
    def is_visible(self) -> bool:
        return self.frame and self.frame.get_visible()

    def show(
        self,
        feature_name: str,
        route: str,
        monitor_id: int,
        dev_mode: bool,
    ):
        self.feature_name = feature_name
        show_frame(self, feature_name, route, monitor_id, dev_mode)

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


def show_frame(
    popup_frame: PopupFrame,
    feature_name: str,
    route: str,
    monitor_id: int,
    dev_mode: bool,
):
    def create_frame():
        popup_frame.frame = Gtk.Window()

        popup_frame.webview = webview(
            feature_name,
            route,
            "popup_frame",
            dev_mode,
            Gdk.RGBA(red=0, green=0, blue=0, alpha=0.0),
            True,
        )
        popup_frame.frame.add(popup_frame.webview)

        layerise_window(popup_frame.frame, f"popup_frame")

        set_layer(
            window=popup_frame.frame,
            monitor_id=monitor_id,
            level=Levels.overlay,
        )

        def on_button_press_event(widget, event: Gdk.EventButton):
            popup_frame.last_button_press_event = event.copy()
            return False

        def on_delete_event(widget, event):
            popup_frame.hide()
            return True

        popup_frame.webview.connect("button-press-event", on_button_press_event)
        popup_frame.frame.connect("delete-event", on_delete_event)
        popup_frame.webview.show()
        popup_frame.frame.hide()

    def show():
        if not popup_frame.is_visible:
            if not popup_frame.frame:
                create_frame()
            else:
                set_layer(
                    window=popup_frame.frame,
                    monitor_id=monitor_id,
                    level=Levels.overlay,
                )
                popup_frame.webview.load_uri(
                    get_uri(feature_name, route, "popup_frame", dev_mode, True)
                )

            GLib.timeout_add(100, popup_frame.frame.show)

    GLib.idle_add(show)


def hide_frame(popup_frame: PopupFrame):
    def hide():
        if popup_frame.is_visible:
            popup_frame.webview.load_html("")
            popup_frame.frame.hide()

    GLib.idle_add(hide)
