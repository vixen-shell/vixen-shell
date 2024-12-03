from vx_features import ParamDataHandler
from vx_types import LevelKeys, AnchorEdgeKeys, AlignmentKeys
from vx_gtk import Gtk, Gdk
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


def set_margins(feature_name: str, frame_id: str):
    if ParamDataHandler.node_is_define(
        f"{feature_name}.frames.{frame_id}.layer_frame.margins"
    ):
        return Margins(
            ParamDataHandler.get_value(
                f"{feature_name}.frames.{frame_id}.layer_frame.margins.top"
            ),
            ParamDataHandler.get_value(
                f"{feature_name}.frames.{frame_id}.layer_frame.margins.right"
            ),
            ParamDataHandler.get_value(
                f"{feature_name}.frames.{frame_id}.layer_frame.margins.bottom"
            ),
            ParamDataHandler.get_value(
                f"{feature_name}.frames.{frame_id}.layer_frame.margins.left"
            ),
        )
    return None


def layerise_frame(frame: Gtk.Window, namespace: str):
    layerise_window(
        window=frame,
        namespace=namespace,
    )


def set_layer_frame(frame: Gtk.Window, feature_name: str, frame_id: str):
    frame.set_size_request(
        ParamDataHandler.get_value(
            f"{feature_name}.frames.{frame_id}.layer_frame.width"
        )
        or -1,
        ParamDataHandler.get_value(
            f"{feature_name}.frames.{frame_id}.layer_frame.height"
        )
        or -1,
    )

    set_layer(
        window=frame,
        monitor_id=ParamDataHandler.get_value(
            f"{feature_name}.frames.{frame_id}.layer_frame.monitor_id"
        ),
        auto_exclusive_zone=ParamDataHandler.get_value(
            f"{feature_name}.frames.{frame_id}.layer_frame.auto_exclusive_zone"
        ),
        exclusive_zone=ParamDataHandler.get_value(
            f"{feature_name}.frames.{frame_id}.layer_frame.exclusive_zone"
        ),
        level=set_level(
            ParamDataHandler.get_value(
                f"{feature_name}.frames.{frame_id}.layer_frame.level"
            )
        ),
        anchor_edges=set_anchor_edges(
            ParamDataHandler.get_value(
                f"{feature_name}.frames.{frame_id}.layer_frame.anchor_edge"
            ),
            ParamDataHandler.get_value(
                f"{feature_name}.frames.{frame_id}.layer_frame.alignment"
            ),
        ),
        margins=set_margins(feature_name, frame_id),
    )
