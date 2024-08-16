# import sys
from vx_features import (
    ParamDataHandler,
    get_root_feature_names,
    RootModule,
    RootFeature,
    RootUtils,
)
from typing import List, Dict
from .Feature import Feature
from .Gtk_main_loop import Gtk_main_loop
from .Gtk_dialog import show_dialog_box
from ..logger import Logger


class DevMode:
    feature_names: list[str] = []

    @staticmethod
    def enable(feature: Feature):
        Logger.add_handler(feature.tty_path, "WARNING", True)
        DevMode.feature_names.append(feature.feature_name)
        Logger.log(f"[Dev mode]: feature '{feature.feature_name}' enabled")

    @staticmethod
    def disable(feature: Feature):
        Logger.remove_handler(feature.tty_path)
        DevMode.feature_names.remove(feature.feature_name)
        Logger.log(f"[Dev mode]: feature '{feature.feature_name}' disabled")

    @staticmethod
    def include(feature: Feature):
        return feature.feature_name in DevMode.feature_names


class Features:
    dict: Dict[str, Feature] = {}

    @staticmethod
    def init():
        Gtk_main_loop.run()

        for name in get_root_feature_names():
            try:
                Features.load(name)
            except:
                pass

        Logger.log(
            f"{'No' if len(Features.dict) == 0 else len(Features.dict)} features initialized"
        )

    @staticmethod
    def load(entry: str, tty_path: str = None):
        try:
            name, feature = Feature.load(entry, tty_path)
        except Exception as exception:
            Logger.log(str(exception), "ERROR")
            show_dialog_box(str(exception), "WARNING")
            raise exception

        if Features.exists(name):
            suffix = " (Dev mode)" if DevMode.include(feature) else ""
            raise KeyError(f"Feature '{name}' already loaded{suffix}")

        if feature.dev_mode:
            DevMode.enable(feature)

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

        if DevMode.include(feature):
            DevMode.disable(feature)

        del Features.dict[name]

        RootUtils.del_instance(name)
        RootFeature.del_instance(name)
        RootModule.del_instance(name)

        ParamDataHandler.remove_param_data(name)

        Logger.log(f"[{name}]: feature unloaded")

        # UNLOAD MODULE
        # if feature.content.sys_path:
        #     modules_to_remove = []

        #     for module in sys.modules.values():
        #         try:
        #             file = getattr(module, "__file__", None)
        #             if not file or not isinstance(file, str):
        #                 continue
        #         except AttributeError:
        #             continue

        #         if any(path in file for path in feature.content.sys_path):
        #             modules_to_remove.append(module.__name__)

        #     for module_name in modules_to_remove:
        #         sys.modules.pop(module_name)

        #     for path in feature.content.sys_path:
        #         while path in sys.path:
        #             sys.path.remove(path)

        # feature_module = sys.modules.get(feature.content.feature_name)
        # if feature_module:
        #     sys.modules.pop(feature.content.feature_name)

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
