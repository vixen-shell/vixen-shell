import subprocess, os, json

from fastapi import WebSocket
from vx_path import VxPath


class VxConfig:
    websockets: list[WebSocket] = []

    API_PORT: int = 6481
    FRONT_PORT: int = 6492
    FRONT_DEV_PORT: int = 5173

    STATE: dict = {"vx_ui_scale": 1.0, "vx_ui_color": "teal", "vx_ui_icons": "regular"}

    @staticmethod
    def gtk_fonts():
        def get_gtk_font_name(monospace: bool = False):
            return (
                subprocess.run(
                    [
                        "gsettings",
                        "get",
                        "org.gnome.desktop.interface",
                        f"{'monospace-' if monospace else ''}font-name",
                    ],
                    stdout=subprocess.PIPE,
                    text=True,
                )
                .stdout.strip()
                .strip("'")
                .rsplit(" ", 1)[0]
            )

        font_family = get_gtk_font_name()
        font_family_monospace = get_gtk_font_name(True)

        return {
            "font_family": font_family,
            "font_family_monospace": font_family_monospace,
        }

    @staticmethod
    def load():
        file_path = VxPath.VX_CONFIG_FILE

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                vx_config: dict = json.load(file)

                VxConfig.API_PORT = vx_config.get("api_port")
                VxConfig.FRONT_PORT = vx_config.get("front_port")
                VxConfig.FRONT_DEV_PORT = vx_config.get("front_dev_port")
                VxConfig.STATE = vx_config.get("state")
        else:
            VxConfig.save()

    @staticmethod
    def save():
        file_path = VxPath.VX_CONFIG_FILE

        data = {
            "api_port": VxConfig.API_PORT,
            "front_port": VxConfig.FRONT_PORT,
            "front_dev_port": VxConfig.FRONT_DEV_PORT,
            "state": VxConfig.STATE,
        }

        if os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        else:
            with open(file_path, "x", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

    @staticmethod
    def update_state(feature_state: dict):
        if any(key not in VxConfig.STATE for key in feature_state):
            VxConfig.STATE.update(feature_state)
            VxConfig.save()
