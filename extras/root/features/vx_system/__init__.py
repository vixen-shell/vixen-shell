from vx_root import feature

feature = feature()

feature.init({"autostart": True, "frames": "disable", "state": "disable"})


@feature.on_startup
def on_startup():
    print("HELLO !!!")


class VXSystem:
    from .actions import Actions
    from .data import Data
    from .files import Files
