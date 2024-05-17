import os
from typing import Callable, Literal
from ...feature_params import (
    root_FeatureParams_dict,
    FeatureParams,
    ParamsError,
)

USER_PARAMS_DIRECTORY = f"{os.path.expanduser('~')}/.config/vixen/features"


class FeatureContent:
    def __init__(self, package_name: str, root_params_dict: root_FeatureParams_dict):
        self.feature_name = package_name
        self.root_params_dict = root_params_dict
        # self.user_params_filepath = f"{USER_PARAMS_DIRECTORY}/{package_name}.json"
        self.user_params_filepath = f"/home/noha/Workflow/final/vixen-shell/config/user/vixen/features/{package_name}.json"
        self.sys_path = None
        self.dev_mode = False

        self.params = None

        self.startup_handler = None
        self.shutdown_handler = None

        self.data_handlers: dict[str, Callable] = {}
        self.action_handlers: dict[str, Callable] = {}
        self.websocket_handlers = {}

        self.contents = {
            "startup": None,
            "shutdown": None,
            "data": {},
            "action": {},
            "socket": {},
        }

    def init_params(self, entry: str):
        try:
            if not entry == self.feature_name:
                self.user_params_filepath = (
                    f"{entry}/config/user/{self.feature_name}.json"
                )
                self.dev_mode = True

            self.params = FeatureParams.create(
                root_params_dict=self.root_params_dict,
                user_filepath=self.user_params_filepath,
                dev_mode=self.dev_mode,
            )
        except ParamsError as params_error:
            raise Exception(f"[{self.feature_name}]: {str(params_error)}")

    def add(self, content_type: Literal["data", "action", "websocket"]):
        def decorator(callback):
            if content_type == "data":
                self.data_handlers[callback.__name__] = callback

            if content_type == "action":
                self.action_handlers[callback.__name__] = callback

            if content_type == "websocket":
                self.websocket_handlers[callback.__name__] = callback

            return callback

        return decorator

    def on_startup(self, callback):
        self.startup_handler = callback
        return callback

    def on_shutdown(self, callback):
        self.shutdown_handler = callback
        return callback

    # def data(self, callback):
    #     self.data_handlers[callback.__name__] = callback
    #     return callback

    # def action(self, callback):
    #     self.action_handlers[callback.__name__] = callback
    #     return callback

    # def websocket(self, callback):
    #     self.websocket_handlers[callback.__name__] = callback
    #     return callback
