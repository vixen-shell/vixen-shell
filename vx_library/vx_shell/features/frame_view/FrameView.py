from .webview import webview
from .layerise_frame import layerise_frame
from ..parameters import FrameParams
from ..Gtk_imports import Gtk


def new_frame(is_layer: bool, feature_name: str, route: str, client_id: str):
    frame = Gtk.Window()
    frame.add(webview(is_layer, feature_name, route, client_id))
    return frame


def create_frame(feature_name: str, client_id: str, frame_params: FrameParams):
    is_layer = bool(frame_params.layer_frame)
    frame = new_frame(is_layer, feature_name, frame_params.route, client_id)

    if not is_layer:
        frame.set_title(frame_params.name)

        if not frame_params.multi_frame:

            def on_delete_event(frame, event):
                frame.hide()
                return True

            frame.connect("delete-event", on_delete_event)
    else:
        layerise_frame(frame, frame_params.name, frame_params.layer_frame)

    if frame_params.multi_frame or frame_params.show_on_startup:
        frame.show_all()

    return frame
