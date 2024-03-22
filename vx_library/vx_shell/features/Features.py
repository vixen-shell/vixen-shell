import os, json
from typing import List, Dict
from fastapi import WebSocket
from pydantic import ValidationError
from .Gtk_main_loop import Gtk_main_loop
from .Feature import Feature
from .parameters import FeatureParams
from ..globals import FEATURE_SETTINGS_DIRECTORY, STARTUP_SETTING_FILE
from ..log import Logger


class Features:
    _features: Dict[str, Feature] = {}

    @staticmethod
    def startup():
        with open(STARTUP_SETTING_FILE, "r", encoding="utf-8") as file:
            startup_list = json.load(file)

        for feature_name in startup_list:
            Features._features[feature_name].start()

    @staticmethod
    def get_params_list() -> List[FeatureParams] | None:
        params: List[FeatureParams] = []

        try:
            for file_name in os.listdir(FEATURE_SETTINGS_DIRECTORY):
                if file_name.endswith(".json"):
                    path = os.path.join(FEATURE_SETTINGS_DIRECTORY, file_name)

                    if os.path.isfile(path):
                        try:
                            params.append(FeatureParams.create(path))
                        except ValidationError as e:
                            error = e.errors()[0]
                            Logger.log("WARNING", f"File: '{path}'")
                            Logger.log(
                                "WARNING",
                                f"{error['type']}: {error['loc']}, {error['msg']}",
                            )
                            Logger.log("ERROR", "Feature not initialized!")
                            return
        except FileNotFoundError as e:
            Logger.log("ERROR", e)
            return

        return params

    @staticmethod
    def init():
        Gtk_main_loop.run()

        params_list = Features.get_params_list()

        if not params_list:
            Gtk_main_loop.quit()
            return False

        for params in params_list:
            feature = Feature(params)
            Features._features[feature.params.name] = feature

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
