from vx_root import feature

feature().init({"autostart": True, "frames": "disable", "state": "disable"})


class VXSystem:
    from .actions import Actions
    from .data import Data
    from .files import Files
