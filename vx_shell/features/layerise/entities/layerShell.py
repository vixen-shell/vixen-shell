from enum import Enum
from vx_gtk import GtkLayerShell


class Levels(Enum):
    background = GtkLayerShell.Layer.BACKGROUND
    bottom = GtkLayerShell.Layer.BOTTOM
    top = GtkLayerShell.Layer.TOP
    overlay = GtkLayerShell.Layer.OVERLAY


class Edges(Enum):
    top = GtkLayerShell.Edge.TOP
    right = GtkLayerShell.Edge.RIGHT
    bottom = GtkLayerShell.Edge.BOTTOM
    left = GtkLayerShell.Edge.LEFT


class Margins:
    def __init__(
        self,
        top: int | None = None,
        right: int | None = None,
        bottom: int | None = None,
        left: int | None = None,
    ):
        self.top: int = top or 0
        self.right: int = right or 0
        self.bottom: int = bottom or 0
        self.left: int = left or 0
