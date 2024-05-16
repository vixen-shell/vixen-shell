from vx_feature_utils import Utils

utils = Utils()

content = utils.define_feature_content(
    {
        "frames": {
            "main": {
                "name": "Ah ah",
                "route": "main",
                "show_on_startup": True,
            },
        },
        "templates": {
            "temp_test": {
                "name": "toto",
                "route": "tintin",
            },
        },
    }
)
