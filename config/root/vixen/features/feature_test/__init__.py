from vx_feature_utils import Utils

utils = Utils.define_feature_utils()
content = Utils.define_feature_content()


@content.on_startup
def on_startup():
    hyprland_feature = utils.features.get("hyprland")
    hyprland_feature.stop()
