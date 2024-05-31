from vx_feature_utils import Utils

utils = Utils.define_feature_utils()
content = Utils.define_feature_content()


@content.on_startup
def on_startup():
    hyprland_feature = utils.features.get("hyprland")
    hyprland_feature.stop()


@content.add_handler("action")
def hello():
    welcome_feature = utils.features.get("welcome")

    if not "about" in welcome_feature.active_frame_ids:
        welcome_feature.open_frame("about")
        print("Hello About !!!")
    else:
        raise Exception("'about' frame already open")
