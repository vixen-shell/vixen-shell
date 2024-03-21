from ..Gtk_imports import Gdk, WebKit2
from ...globals import get_front_url, DevMode


def webview(is_layer: bool, feature_name: str, route: str, client_id: str):
    def webKit_settings():
        settings = WebKit2.Settings()
        settings.set_property(
            "hardware_acceleration_policy", WebKit2.HardwareAccelerationPolicy.ALWAYS
        )
        settings.set_property("enable-developer-extras", True)
        return settings

    webview = WebKit2.WebView()
    webview.set_settings(webKit_settings())
    webview.load_uri(
        f"{get_front_url()}/?feature={feature_name}&route={route}&client_id={client_id}"
    )

    if is_layer:
        webview.set_background_color(Gdk.RGBA(red=0, green=0, blue=0, alpha=0.0))

    if not DevMode.is_active:

        def on_context_menu(webview, context_menu, event, hit_test_result):
            return True

        webview.connect("context-menu", on_context_menu)

    return webview
