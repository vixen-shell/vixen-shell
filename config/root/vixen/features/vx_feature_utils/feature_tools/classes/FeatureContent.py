import os, json
from typing import Callable, Literal
from ...feature_params import (
    root_FeatureParams_dict,
    FeatureParams,
    ParamsError,
)

USER_PARAMS_DIRECTORY = f"{os.path.expanduser('~')}/.config/vixen/features"
ContentType = Literal["action", "data", "socket"]


class Contents:
    def __init__(self):
        self.action: dict[str, Callable] = {}
        self.data: dict[str, Callable] = {}
        self.socket: dict[str, Callable] = {}

        self.shutdown: Callable = None
        self.startup: Callable = None


class FeatureContent:
    def __init__(self, package_name: str, root_params_dict: root_FeatureParams_dict):
        self.feature_name = package_name
        self.root_params_dict = root_params_dict
        self.sys_path = None
        self.dev_mode = False

        self.params: FeatureParams = None

        self.contents = Contents()

    def init_params(self, entry: str):
        # user_params_filepath = f"{USER_PARAMS_DIRECTORY}/{self.feature_name}.json"
        user_params_filepath = f"/home/noha/Workflow/final/vixen-shell/config/user/vixen/features/{self.feature_name}.json"

        try:
            if not entry == self.feature_name:
                user_params_filepath = f"{entry}/config/user/{self.feature_name}.json"
                self.dev_mode = True

            self.params = FeatureParams.create(
                root_params_dict=self.root_params_dict,
                user_params_filepath=user_params_filepath,
                dev_mode=self.dev_mode,
            )

        except ParamsError as params_error:
            raise Exception(f"[{self.feature_name}]: {str(params_error)}")

    def add(self, content_type: ContentType):
        def decorator(callback: Callable):
            try:
                sub_contents: dict = getattr(self.contents, content_type)
            except AttributeError as attribute_error:
                callback_filename = callback.__code__.co_filename
                callback_line_number = callback.__code__.co_firstlineno
                raise Exception(
                    f"Content type '{content_type}' not exists: Error in file '{callback_filename}' (line: {str(callback_line_number)})"
                )

            if sub_contents.get(callback.__name__):
                raise Exception(
                    f"Feature already has content of type '{content_type}' named '{callback.__name__}'"
                )

            sub_contents[callback.__name__] = callback
            return callback

        return decorator

    def get(self, content_type: ContentType, name: str):
        sub_contents: dict = getattr(self.contents, content_type)
        return sub_contents[name]

    def on_startup(self, callback: Callable):
        if self.contents.startup:
            callback_filename = callback.__code__.co_filename
            callback_line_number = callback.__code__.co_firstlineno
            raise Exception(
                f"Feature already has a startup sequence: Error in file '{callback_filename}' (line: {str(callback_line_number)})"
            )

        self.contents.startup = callback
        return callback

    def on_shutdown(self, callback: Callable):
        if self.contents.shutdown:
            callback_filename = callback.__code__.co_filename
            callback_line_number = callback.__code__.co_firstlineno
            raise Exception(
                f"Feature already has a shutdown sequence: Error in file '{callback_filename}' (line: {str(callback_line_number)})"
            )

        self.contents.shutdown = callback
        return callback

    def startup_sequence(self):
        if self.contents.startup:
            self.contents.startup()

    def shutdown_sequence(self):
        if self.contents.shutdown:
            self.contents.shutdown()
