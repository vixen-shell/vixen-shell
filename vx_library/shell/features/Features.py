from vx_feature_utils import Utils
from typing import List, Dict
from .Feature import Feature
from .Gtk_main_loop import Gtk_main_loop
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
        if DevMode.feature_name and DevMode.feature_name == feature.name:
            DevMode.disable()

        if not DevMode.feature_name and feature.dev_mode:
            DevMode.enable(feature.name)


class Features:
    dict: Dict[str, Feature] = {}

    @staticmethod
    def init():
        Gtk_main_loop.run()

        for name in Utils.get_feature_names():
            try:
                Features.load(name)

            except Exception as exception:
                Logger.log(exception, "WARNING")

        Logger.log(
            f"{'No' if len(Features.dict) == 0 else len(Features.dict)} features initialized"
        )

    @staticmethod
    def load(entry: str):
        name, feature = Feature.load(entry)

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
