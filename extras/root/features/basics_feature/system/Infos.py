import os, gi

gi.require_version("PangoCairo", "1.0")
from gi.repository import PangoCairo


class SystemInfos:
    @staticmethod
    def user_name() -> str:
        return os.getlogin()

    @staticmethod
    def user_directory() -> str:
        return os.path.expanduser("~")

    @staticmethod
    def available_fonts(monospace: bool = False) -> list[str]:
        font_map = PangoCairo.FontMap.get_default()
        families = font_map.list_families()
        font_names = (
            [family.get_name() for family in families]
            if not monospace
            else [family.get_name() for family in families if family.is_monospace()]
        )
        return font_names
