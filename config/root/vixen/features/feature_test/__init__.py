from vx_feature_utils import define_feature

feature = define_feature(
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
