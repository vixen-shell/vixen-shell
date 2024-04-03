from typing import List, Dict
from fastapi import WebSocket
from .Gtk_main_loop import Gtk_main_loop
from .Feature import Feature
from .parameters import Parameters
from ..log import Logger


class Features:
    _features: Dict[str, Feature] = {}
    _dev_feature: str = None

    @staticmethod
    def startup():
        for feature_name in Parameters.get_startup_list():
            Features._features[feature_name].start()

    @staticmethod
    def init():
        Gtk_main_loop.run()

        parameter_list = Parameters.get_feature_parameter_list()

        if not parameter_list:
            Logger.log("ERROR", "Unable to load Vixen Shell config")
            Gtk_main_loop.quit()
            return False

        for params in parameter_list:
            feature = Feature(params)
            Features._features[params.name] = feature

        return True

    @staticmethod
    async def cleanup():
        for feature_name in Features._features:
            feature = Features.get(feature_name)
            if feature.is_started:
                await feature.stop()

        Features._features = {}
        Gtk_main_loop.quit()

    @staticmethod
    def init_dev_feature(dev_dir: str) -> tuple[str | None, str | None]:
        if Features._dev_feature:
            return None, "Development mode is already in use"

        package = Parameters.read(f"{dev_dir}/package.json")

        if not package:
            return None, f"Unable to found 'package.json' file in '{dev_dir}' directory"

        feature_name = package.get("name")

        if not feature_name:
            return None, "Unable to found 'name' property in 'package.json' file"

        if Features.key_exists(feature_name):
            return None, f"A feature called '{feature_name}' already exists"

        params = Parameters.get_feature_parameters(
            f"{dev_dir}/config/root/{feature_name}.json",
            f"{dev_dir}/config/user/{feature_name}.json",
        )

        if not params:
            return None, f"Unable to load '{feature_name}' feature config"

        feature = Feature(params, True)
        Features._features[params.name] = feature

        Features._dev_feature = params.name
        return feature_name, None

    @staticmethod
    async def remove_dev_feature() -> tuple[str | None, str | None]:
        feature_name = Features._dev_feature

        if not feature_name:
            return None, "Development mode is not in use"

        await Features._features[feature_name].stop()
        del Features._features[feature_name]
        Features._dev_feature = None
        return feature_name, None

    @staticmethod
    def keys() -> List[str]:
        return list(Features._features.keys())

    @staticmethod
    def key_exists(feature_name: str) -> bool:
        return feature_name in Features._features

    @staticmethod
    def get(feature_name: str) -> Feature | None:
        if Features.key_exists(feature_name):
            return Features._features[feature_name]

    @staticmethod
    async def connect_client(
        feature_name: str, client_id: str, websocket: WebSocket
    ) -> Feature | None:
        reason = None

        if not Features.key_exists(feature_name):
            reason = f"Feature '{feature_name}' not found"
        else:
            feature = Features.get(feature_name)
            if not feature.pipe_is_opened:
                reason = f"Feature '{feature_name}' pipe is closed"

        if reason:
            await websocket.close(reason=reason)
            return

        client_connected = await feature.connect_client(client_id, websocket)
        if client_connected:
            return feature
