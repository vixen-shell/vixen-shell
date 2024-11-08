from vx_config import VxConfig
from vx_gtk import WebKit2
from vx_logger import Logger


def get_front_port(dev_mode: bool):
    return VxConfig.FRONT_PORT if not dev_mode else VxConfig.FRONT_DEV_PORT


def get_uri(
    feature_name: str, route: str, frame_id: str, dev_mode: bool, popup: bool = False
):

    def get_params():
        feature_param = f"feature={feature_name}"
        route_param = f"route={route}"
        frame_param = f"frame={frame_id}"

        return f"{feature_param}&{route_param}&{frame_param}{'&popup' if popup else ''}"

    return f"http://localhost:{get_front_port(dev_mode)}/?{get_params()}"


def webview(
    feature_name: str,
    route: str,
    frame_id: str,
    dev_mode: bool,
    background_color,
    popup=False,
):
    def on_decide_policy(webview, decision, decision_type):
        if isinstance(decision, WebKit2.NavigationPolicyDecision):
            request = decision.get_request()
            uri = request.get_uri()
            allowed_domain = f"localhost:{get_front_port(dev_mode)}"

            if uri == "about:blank" or allowed_domain in uri:
                return False
            else:
                Logger.log(f"Uri not allowed: {uri}", "WARNING")
                decision.ignore()
                return True

        return False

    def on_context_menu(webview, context_menu, event, hit_test_result):
        return False if dev_mode else True

    webview = WebKit2.WebView()

    if dev_mode:
        webview.get_settings().set_enable_developer_extras(True)

    webview.connect("context-menu", on_context_menu)
    webview.connect("decide-policy", on_decide_policy)
    webview.set_background_color(background_color)

    webview.load_uri(get_uri(feature_name, route, frame_id, dev_mode, popup))

    return webview
