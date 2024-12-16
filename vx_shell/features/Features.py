from vx_features import FeatureUtils
from typing import List, Dict
from vx_logger import Logger
from .Feature import Feature
from .FeatureLoader import FeatureLoader


class Features:
    __dict: Dict[str, Feature] = {}

    @staticmethod
    def init():
        for name in FeatureUtils.get_root_feature_names():
            try:
                Features.load(name)
            except:
                pass

        Logger.log(
            f"{'No' if len(Features.__dict) == 0 else len(Features.__dict)} features initialized"
        )

    @staticmethod
    def load(entry: str, tty_path: str = None):
        name, feature = Feature.load(entry, tty_path)

        Features.__dict[name] = feature
        Logger.log(f"[{name}]: feature loaded")

        return name, feature.is_started

    @staticmethod
    async def unload(name: str, for_remove: bool = False):
        feature = Features.get(name)

        if not feature:
            raise KeyError(f"'{name}' feature not found")

        if feature.is_started or feature.is_active:
            await feature.stop()

        del Features.__dict[name]
        FeatureLoader(name).unload(for_remove)
        FeatureLoader.del_instance(name)

        Logger.log(f"[{name}]: feature unloaded")

    @staticmethod
    async def stop():
        for feature in Features.__dict.values():
            if feature.is_started:
                await feature.stop(cleanup_frame=False)

    @staticmethod
    def names() -> List[str]:
        return list(Features.__dict.keys())

    @staticmethod
    def exists(name: str) -> bool:
        return name in Features.__dict

    @staticmethod
    def get(name: str) -> Feature | None:
        return Features.__dict.get(name)
