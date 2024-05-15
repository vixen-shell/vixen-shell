from typing import Callable
from .AbstractLogger import Logger
from ...utils import USER_PARAMS_DIRECTORY
from ...feature_params import (
    root_FeatureParams_dict,
    FeatureParams,
    ParamsError,
)


class FeatureContent:
    def __init__(self, package_name: str, root_params_dict: root_FeatureParams_dict):
        self.feature_name = package_name
        self.root_params_dict = root_params_dict
        self.dev_user_params_filepath = None
        self.logger: Logger = None

        self.startup_handler = None
        self.shutdown_handler = None

        self.data_handlers: dict[str, Callable] = {}
        self.action_handlers: dict[str, Callable] = {}
        self.websocket_handlers = {}

    def on_startup(self, callback):
        self.startup_handler = callback
        return callback

    def on_shutdown(self, callback):
        self.shutdown_handler = callback
        return callback

    def data(self, callback):
        self.data_handlers[callback.__name__] = callback
        return callback

    def action(self, callback):
        self.action_handlers[callback.__name__] = callback
        return callback

    def websocket(self, callback):
        self.websocket_handlers[callback.__name__] = callback
        return callback

    def get_params(self):
        try:
            return FeatureParams.create(
                root_params_dict=self.root_params_dict,
                user_filepath=(
                    f"{USER_PARAMS_DIRECTORY}/{self.feature_name}.json"
                    if not self.dev_user_params_filepath
                    else self.dev_user_params_filepath
                ),
                dev_mode=bool(self.dev_user_params_filepath),
            )
        except ParamsError as params_error:
            raise Exception(f"[{self.feature_name}]: {str(params_error)}")
