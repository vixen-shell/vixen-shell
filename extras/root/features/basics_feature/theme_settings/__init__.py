from vx_root import root_content, State
from ..system import System

content = root_content()

theme_settings_frame = {
    "name": "Vixen Shell Theme Settings",
    "route": "vx_theme",
    "layer_frame": "disable",
}

content.dispatch("data", "available_fonts")(System.Infos.available_fonts)


@content.dispatch("task")
def restore_theme_settings(settings: dict):
    for key in settings:
        State.set(key, settings[key])


@content.dispatch("task")
def save_theme_setting(keys: list[str]):
    State.save_items(keys)
