from vx_feature_utils import Utils

# utils = Utils.define_feature_utils()
content = Utils.define_feature_content(
    {"autostart": True, "frames": "disable", "state": "disable"}
)


class VXSystem:
    from .actions import Actions
    from .data import Data
    from .files import Files
