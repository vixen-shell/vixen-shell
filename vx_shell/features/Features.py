from vx_features import FeatureUtils
from typing import List, Dict
from .Feature import Feature
from .FeatureLoader import FeatureLoader
from .Gtk_main_loop import Gtk_main_loop
from ..logger import Logger


class Features:
    dict: Dict[str, Feature] = {}

    @staticmethod
    def init():
        Gtk_main_loop.run()

        for name in FeatureUtils.get_root_feature_names():
            try:
                Features.load(name)
            except:
                pass

        Logger.log(
            f"{'No' if len(Features.dict) == 0 else len(Features.dict)} features initialized"
        )

    @staticmethod
    def load(entry: str, tty_path: str = None):
        name, feature = Feature.load(entry, tty_path)

        Features.dict[name] = feature
        Logger.log(f"[{name}]: feature loaded")

        return name, feature.is_started

    @staticmethod
    async def unload(name: str):
        feature = Features.get(name)

        if not feature:
            raise KeyError(f"'{name}' feature not found")

        if feature.is_started:
            await feature.stop()

        del Features.dict[name]
        FeatureLoader(name).unload()
        FeatureLoader.del_instance(name)

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
