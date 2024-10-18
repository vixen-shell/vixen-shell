"""
Author            : Nohavye
Author's Email    : noha.poncelet@gmail.com
Repository        : https://github.com/vixen-shell/vixen-shell.git
Description       : vixen shell api features layerise library.
License           : GPL3
"""

from typing import List, Literal
from vx_gtk import Gdk, Gtk, GtkLayerShell
from .entities import Levels, Edges, Margins


def init_for_window(window: Gtk.Window):
    GtkLayerShell.init_for_window(window)


def set_namespace(window: Gtk.Window, namespace: str):
    GtkLayerShell.set_namespace(window, namespace)


def set_monitor(window: Gtk.Window, monitor_id: int | None):
    if not monitor_id:
        monitor_id = 0

    GtkLayerShell.set_monitor(window, Gdk.Display.get_default().get_monitor(monitor_id))


def set_exclusive_zone(window: Gtk.Window, auto: bool, exclusive_zone: int | None):
    if not exclusive_zone:
        exclusive_zone = 0
    if auto:
        GtkLayerShell.auto_exclusive_zone_enable(window)
    else:
        GtkLayerShell.set_exclusive_zone(window, exclusive_zone)


def set_level(window: Gtk.Window, level: Levels | None):
    if not level:
        level = Levels.background
    GtkLayerShell.set_layer(window, level.value)


def unset_anchor_edges(window: Gtk.Window):
    for edge in Edges:
        GtkLayerShell.set_anchor(window, edge.value, False)


def set_anchor_edges(window: Gtk.Window, anchor_edges: List[Edges] | None):
    if not anchor_edges:
        anchor_edges = [Edges.top, Edges.right, Edges.bottom, Edges.left]
    unset_anchor_edges(window)

    for edge in anchor_edges:
        GtkLayerShell.set_anchor(window, edge.value, True)


def set_margin(
    window: Gtk.Window,
    margin: Literal["top", "right", "bottom", "left"],
    value: int = 0,
):
    GtkLayerShell.set_margin(window, getattr(Edges, margin).value, value)


def unset_margins(window: Gtk.Window):
    margins_attr = ["top", "right", "bottom", "left"]

    for attr in margins_attr:
        set_margin(window, attr)


def set_margins(window: Gtk.Window, margins: Margins | None):
    if not margins:
        margins = Margins()
    margins_attr = ["top", "right", "bottom", "left"]

    for attr in margins_attr:
        set_margin(window, attr, getattr(margins, attr))


def layerise_window(
    window: Gtk.Window,
    namespace: str,
    monitor_id: int | None = None,
    auto_exclusive_zone: bool = False,
    exclusive_zone: int | None = None,
    level: Levels | None = None,
    anchor_edges: List[Edges] | None = None,
    margins: Margins | None = None,
):
    init_for_window(window)
    set_namespace(window, namespace)

    set_layer(
        window,
        monitor_id,
        auto_exclusive_zone,
        exclusive_zone,
        level,
        anchor_edges,
        margins,
    )


def set_layer(
    window: Gtk.Window,
    monitor_id: int | None = None,
    auto_exclusive_zone: bool = False,
    exclusive_zone: int | None = None,
    level: Levels | None = None,
    anchor_edges: List[Edges] | None = None,
    margins: Margins | None = None,
):
    set_monitor(window, monitor_id)
    set_exclusive_zone(window, auto_exclusive_zone, exclusive_zone)
    set_level(window, level)
    set_anchor_edges(window, anchor_edges)
    set_margins(window, margins)
