from vx_types import LevelKeys, AnchorEdgeKeys, AlignmentKeys
from vx_gtk import Gtk
from .frame_utils import FrameParams
from ..layerise import Edges, Levels, Margins, layerise_window, set_layer

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


def set_margins(params: FrameParams):
    if params.node_is_define("layer_frame.margins"):
        return Margins(
            params("layer_frame.margins.top"),
            params("layer_frame.margins.right"),
            params("layer_frame.margins.bottom"),
            params("layer_frame.margins.left"),
        )
    return None


def layerise_frame(frame: Gtk.Window):
    params: FrameParams = frame.params

    layerise_window(
        window=frame,
        namespace=f"vx_layer_{params("name")}",
    )


def set_layer_frame(frame: Gtk.Window):
    params: FrameParams = frame.params

    frame.set_size_request(
        params("layer_frame.width") or -1,
        params("layer_frame.height") or -1,
    )

    set_layer(
        window=frame,
        monitor_id=params("layer_frame.monitor_id"),
        auto_exclusive_zone=params("layer_frame.auto_exclusive_zone"),
        exclusive_zone=params("layer_frame.exclusive_zone"),
        level=set_level(params("layer_frame.level")),
        anchor_edges=set_anchor_edges(
            params("layer_frame.anchor_edge"),
            params("layer_frame.alignment"),
        ),
        margins=set_margins(params),
    )
