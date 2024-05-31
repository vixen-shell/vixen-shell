import sys
from vx_feature_utils import Utils
from typing import List, Dict
from .Feature import Feature
from .Gtk_main_loop import Gtk_main_loop
from .Gtk_dialog import show_dialog
from ..logger import Logger


class DevMode:
    feature_name: str = None

    @staticmethod
    def enable(feature_name: str):
        if DevMode.feature_name:
            raise ValueError("Development mode already in use")

        DevMode.feature_name = feature_name
        Logger.log("[Dev mode]: enabled")

    @staticmethod
    def disable():
        if not DevMode.feature_name:
            Logger.log("[Dev mode]: not in use", "WARNING")

        DevMode.feature_name = None
        Logger.log("[Dev mode]: disabled")

    @staticmethod
    def toggle(feature: Feature):
        if not DevMode.feature_name and feature.content.dev_mode:
            DevMode.enable(feature.content.feature_name)

        elif (
            DevMode.feature_name
            and DevMode.feature_name == feature.content.feature_name
        ):
            sys.path.remove(feature.content.sys_path)
            DevMode.disable()


class Features:
    dict: Dict[str, Feature] = {}

    @staticmethod
    def init():
        Gtk_main_loop.run()

        for name in Utils.get_root_feature_names():
            try:
                Features.load(name)

            except Exception as exception:
                Logger.log(str(exception), "WARNING")
                show_dialog(str(exception), "WARNING")

        Logger.log(
            f"{'No' if len(Features.dict) == 0 else len(Features.dict)} features initialized"
        )

    @staticmethod
    def load(entry: str):
        try:
            name, feature = Feature.load(entry)
        except Exception as exception:
            Logger.log(str(exception), "ERROR")
            raise exception

        if Features.exists(name):
            suffix = " in development mode" if DevMode.feature_name == name else ""
            raise KeyError(f"Feature '{name}' already loaded{suffix}")

        DevMode.toggle(feature)

        Features.dict[name] = feature
        Logger.log(f"[{name}]: feature loaded")

        return name, feature.is_started

    @staticmethod
    async def unload(name: str):
        feature = Features.get(name)

        if not feature:
            raise KeyError(f"'{name}' feature not found")

        DevMode.toggle(feature)

        if feature.is_started:
            await feature.stop()

        del Features.dict[name]
        Logger.log(f"[{name}]: feature unloaded")

    @staticmethod
    async def stop():
        for feature in Features.dict.values():
            if feature.is_started:
                await feature.stop()

        Gtk_main_loop.quit()

    @staticmethod
    def names() -> List[str]:
        return list(Features.dict.keys())

    @staticmethod
    def exists(name: str) -> bool:
        return name in Features.dict

    @staticmethod
    def get(name: str) -> Feature | None:
        return Features.dict.get(name)
