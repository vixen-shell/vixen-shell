from ..layerise import Edges, Levels, Margins, layerise_window
from ..parameters import LevelKeys, AnchorEdgeKeys, AlignmentKeys, MarginParams
from ..parameters import LayerFrameParams
from ..Gtk_imports import Gtk, Gdk

anchor_key_values = {
    "top_start": [Edges.top, Edges.left],
    "top_center": [Edges.top],
    "top_end": [Edges.top, Edges.right],
    "top_stretch": [Edges.top, Edges.left, Edges.right],
    "right_start": [Edges.right, Edges.top],
    "right_center": [Edges.right],
    "right_end": [Edges.right, Edges.bottom],
    "right_stretch": [Edges.right, Edges.top, Edges.bottom],
    "bottom_start": [Edges.bottom, Edges.left],
    "bottom_center": [Edges.bottom],
    "bottom_end": [Edges.bottom, Edges.right],
    "bottom_stretch": [Edges.bottom, Edges.left, Edges.right],
    "left_start": [Edges.left, Edges.top],
    "left_center": [Edges.left],
    "left_end": [Edges.left, Edges.bottom],
    "left_stretch": [Edges.left, Edges.top, Edges.bottom],
    "full_center": None,
    "full_stretch": [Edges.top, Edges.right, Edges.bottom, Edges.left],
}


def set_level(level_key: LevelKeys | None):
    try:
        return getattr(Levels, level_key)
    except:
        return None


def set_anchor_edges(
    anchor_edge_key: AnchorEdgeKeys | None, alignment_key: AlignmentKeys | None
):
    if not anchor_edge_key:
        anchor_edge_key = "full"
    if not alignment_key:
        alignment_key = "center"

    return anchor_key_values.get(f"{anchor_edge_key}_{alignment_key}")


def set_margins(margin_params: MarginParams | None):
    if margin_params:
        return Margins(
            margin_params.get("top"),
            margin_params.get("right"),
            margin_params.get("bottom"),
            margin_params.get("left"),
        )
    return None


def layerise_frame(
    frame: Gtk.Window, namespace: str, layer_frame_params: LayerFrameParams
):
    frame.set_app_paintable(True)

    frame.set_size_request(
        layer_frame_params.width or -1, layer_frame_params.height or -1
    )

    layerise_window(
        window=frame,
        namespace=namespace,
        monitor_id=layer_frame_params.monitor_id,
        auto_exclusive_zone=layer_frame_params.auto_exclusive_zone,
        exclusive_zone=layer_frame_params.exclusive_zone,
        level=set_level(layer_frame_params.level),
        anchor_edges=set_anchor_edges(
            layer_frame_params.anchor_edge, layer_frame_params.alignment
        ),
        margins=set_margins(layer_frame_params.margins),
    )
