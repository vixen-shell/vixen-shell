from typing import List, Dict
from fastapi import WebSocket
from .Feature import Feature
from .parameters import ParamsFiles
from .Gtk_main_loop import Gtk_main_loop


class Features:
    _dict: Dict[str, Feature] = {}
    _dev_name: str = None

    @staticmethod
    def init():
        Gtk_main_loop.run()

        for name in ParamsFiles.get_feature_names():
            Features.add(Feature.from_name(name))

        return True

    @staticmethod
    def add(feature: Feature):
        if Features.exists(feature.name):
            raise ValueError(f"A feature called '{feature.name}' already exists")

        Features._dict[feature.name] = feature

    @staticmethod
    async def remove(name: str):
        feature = Features.get(name)

        if feature and feature.is_started:
            await feature.stop()
            del Features._dict[name]

    @staticmethod
    async def stop():
        Gtk_main_loop.quit()

    @staticmethod
    def init_dev(directory: str) -> tuple[str | None, str | None]:
        if Features._dev_name:
            return None, "Development mode is already in use"

        try:
            feature = Feature.from_dev_directory(directory)
            Features.add(feature)
            Features._dev_name = feature.name
        except Exception as exception:
            return None, exception

        return Features._dev_name, None

    @staticmethod
    async def remove_dev() -> tuple[str | None, str | None]:
        if not Features._dev_name:
            return None, "Development mode is not in use"

        await Features.remove(Features._dev_name)
        Features._dev_name = None
        return Features._dev_name, None

    @staticmethod
    def names() -> List[str]:
        return list(Features._dict.keys())

    @staticmethod
    def exists(name: str) -> bool:
        return name in Features._dict

    @staticmethod
    def get(name: str) -> Feature | None:
        return Features._dict.get(name)
