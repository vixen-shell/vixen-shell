import os, json
from typing import List, Dict
from fastapi import WebSocket
from pydantic import ValidationError
from .Gtk_main_loop import Gtk_main_loop
from .Feature import Feature
from .parameters import FeatureParams, Parameters
from ..globals import USER_CONFIG_DIRECTORY
from ..log import Logger


class Features:
    _features: Dict[str, Feature] = {}

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
