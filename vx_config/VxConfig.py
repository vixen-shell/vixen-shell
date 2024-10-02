import subprocess, os, json

from vx_path import VxPath


class VxConfig:
    API_PORT: int = 6481
    FRONT_PORT: int = 6492
    FRONT_DEV_PORT: int = 5173
    UI_SCALE: float = 1.0
    UI_COLOR: str = "teal"
    UI_ICONS: str = "regular"

    @staticmethod
    def gtk_fonts():
        def get_gtk_font_name(monospace: bool = False):
            return subprocess.run(
                [
                    "gsettings",
                    "get",
                    "org.gnome.desktop.interface",
                    f"{"monospace-" if monospace else ""}font-name",
                ],
                stdout=subprocess.PIPE,
                text=True,
            ).stdout.strip().strip("'").rsplit(" ", 1)[0]

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
                VxConfig.UI_SCALE = vx_config.get("ui_scale")
                VxConfig.UI_COLOR = vx_config.get("ui_color")
                VxConfig.UI_ICONS = vx_config.get("ui_icons")
        else:
            VxConfig.save()

    @staticmethod
    def save():
        file_path = VxPath.VX_CONFIG_FILE

        data = {
            "api_port": VxConfig.API_PORT,
            "front_port": VxConfig.FRONT_PORT,
            "front_dev_port": VxConfig.FRONT_DEV_PORT,
            "ui_scale": VxConfig.UI_SCALE,
            "ui_color": VxConfig.UI_COLOR,
            "ui_icons": VxConfig.UI_ICONS,
        }

        if os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        else:
            with open(file_path, "x", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
