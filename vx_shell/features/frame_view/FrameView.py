from vx_feature_utils import FrameParams
from .layerise_frame import layerise_frame
from ..Gtk_imports import GLib, Gtk, Gdk, WebKit2
from ...globals import FRONT_PORT, FRONT_DEV_PORT


def get_frame_uri(feature_name: str, route: str, dev_mode: bool):
    def get_front_port(dev_mode: bool):
        return FRONT_PORT if not dev_mode else FRONT_DEV_PORT

    def get_params():
        feature_param = f"feature={feature_name}"
        route_param = f"route={route}"

        return f"{feature_param}&{route_param}"

    return f"http://localhost:{get_front_port(dev_mode)}/?{get_params()}"


def webview(uri: str, dev_mode: bool):
    def on_context_menu(webview, context_menu, event, hit_test_result):
        return False if dev_mode else True

    webview = WebKit2.WebView()

    if dev_mode:
        settings = WebKit2.Settings()
        settings.set_property("enable-developer-extras", True)
        webview.set_settings(settings)

    webview.set_background_color(Gdk.RGBA(red=0, green=0, blue=0, alpha=0.0))
    webview.connect("context-menu", on_context_menu)
    webview.load_uri(uri)

    return webview


def fade_in(window, current_opacity):
    current_opacity += 0.05
    window.set_opacity(current_opacity)
    if current_opacity < 1:
        GLib.timeout_add(30, fade_in, window, current_opacity)


class FrameView:
    def __init__(
        self,
        feature_name: str,
        frame_params: FrameParams,
        dev_mode: bool = False,
    ):
        self.is_first_render = True
        self.feature_name = feature_name
        self.route = frame_params.route
        self.dev_mode = dev_mode
        self.frame_uri = get_frame_uri(self.feature_name, self.route, self.dev_mode)

        def process():
            self.frame = Gtk.Window()

            def on_load_changed(webview, load_event):
                if load_event == WebKit2.LoadEvent.FINISHED:
                    GLib.timeout_add(200, self.frame.queue_draw)

            web_view = webview(self.frame_uri, self.dev_mode)
            web_view.connect("load-changed", on_load_changed)
            self.frame.add(web_view)

            self.frame.connect(
                "delete-event", lambda frame, event: (self.hide(), True)[1]
            )

            if bool(frame_params.layer_frame):
                self.frame.set_app_paintable(True)
                layerise_frame(self.frame, frame_params.name, frame_params.layer_frame)
            else:
                self.frame.set_title(frame_params.name)

            self.frame.realize()

        GLib.idle_add(process)

        if frame_params.show_on_startup:
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
