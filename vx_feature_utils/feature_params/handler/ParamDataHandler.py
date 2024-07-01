import copy
from typing import Literal, Any, Callable
from pydantic import ValidationError
from ..classes import RootBuilder, ParamsValidationError
from ..utils import read_json, write_json
from ..models import (
    root_FeatureParams_dict,
    user_FeatureParams_dict,
    root_FeatureParams,
    user_FeatureParams,
)

Permission = Literal["DISABLED", "ROOT", "RESTRICTED", "USER"]


class ParamData:
    def __init__(
        self,
        root_params_dict: root_FeatureParams_dict,
        user_params_filepath: str,
        dev_mode: bool = False,
    ) -> None:
        try:
            root_params = root_FeatureParams(**root_params_dict)
        except ValidationError as validation_error:
            raise ParamsValidationError(
                title="Validation error in root parameters",
                validation_error=validation_error,
            )

        try:
            user_params = user_FeatureParams(**read_json(user_params_filepath) or {})
        except ValidationError as validation_error:
            raise ParamsValidationError(
                title=f"Validation error in '{user_params_filepath}'",
                validation_error=validation_error,
            )

        params_builder = RootBuilder(
            root_params.model_copy(), user_params.model_copy(), user_params_filepath
        )

        new_root_params_dict = params_builder.build()

        self.root: root_FeatureParams_dict = new_root_params_dict
        self.user: user_FeatureParams_dict = user_params.model_dump(exclude_none=True)
        self.user_filepath: str = user_params_filepath
        self.dev_mode: bool = dev_mode

        print(self.user["state"])


class ParamException(Exception):
    def __init__(self, path: str, type: Permission | Literal["NODE", "VALUE"]) -> None:
        if type == "DISABLED":
            message = "Disabled parameter, cannot define user value"
        if type == "ROOT":
            message = "Root definition, cannot define user value"
        if type == "RESTRICTED":
            message = "Root definition, bad user value"
        if type == "NODE":
            message = "The path returns a node"
        if type == "VALUE":
            message = "The path returns a value"

        message = f"{message} ({path})"

        super().__init__(message)
        self.param_type = type


def get_dict(node: dict, path_keys: list[str]) -> dict | Any | None:
    for key in path_keys:
        try:
            node = node[key]
        except KeyError:
            return
    return node


def set_dict(node: dict, path_keys: list[str], value) -> None:
    for key in path_keys[:-1]:
        node = node.setdefault(key, {})
    node[path_keys[-1]] = value


def break_path(path: str):
    feature_name, *path_keys = path.split(".")
    return feature_name, path_keys


def get_permission(feature_name: str, path_keys: list[str]) -> Permission:
    node = ParamDataHandler.select_data(feature_name, "ROOT")

    for key in path_keys:
        node = node.get(key)

        if node is None:
            return "USER"
        if node == "disable":
            return "DISABLED"
        if isinstance(node, list):
            return "RESTRICTED"

    return "ROOT"


def is_value(path_keys: str) -> bool:
    value = get_dict(user_FeatureParams_dict.get_structure(), path_keys)
    if isinstance(value, dict):
        return False
    return True


class ParamDataHandler:
    __data_dict: dict[str, ParamData] = {}
    __listeners: dict[str, list[Callable[[Any], None]]] = {}

    @staticmethod
    def add_param_data(feature_name: str, param_data: ParamData):
        ParamDataHandler.__data_dict[feature_name] = param_data

    @staticmethod
    def remove_param_data(feature_name: str):
        ParamDataHandler.__data_dict.pop(feature_name)

    @staticmethod
    def add_param_listener(path: str, listener: Callable[[Any], None]):
        path_listeners = ParamDataHandler.__listeners.get(path)

        if path_listeners:
            path_listeners.append(listener)
        else:
            ParamDataHandler.__listeners[path] = [listener]

    @staticmethod
    def remove_param_listener(path: str, listener: Callable[[Any], None]):
        path_listeners = ParamDataHandler.__listeners.get(path)

        if path_listeners:
            path_listeners.remove(listener)

            if len(path_listeners) == 0:
                ParamDataHandler.__listeners.pop(path)

    @staticmethod
    def select_data(
        feature_name: str, type: Literal["ROOT", "USER"]
    ) -> root_FeatureParams_dict | user_FeatureParams_dict:
        return getattr(ParamDataHandler.__data_dict[feature_name], type.lower())

    @staticmethod
    def node_is_define(path: str) -> bool:
        feature_name, path_keys = break_path(path)

        if is_value(path_keys):
            raise ParamException(path, "VALUE")

        permission = get_permission(feature_name, path_keys)

        if permission == "DISABLED":
            return False
        if permission == "ROOT":
            node = get_dict(
                ParamDataHandler.select_data(feature_name, "ROOT"), path_keys
            )
        if permission == "USER":
            node = get_dict(
                ParamDataHandler.select_data(feature_name, "USER"), path_keys
            )

        return bool(node)

    @staticmethod
    def get_frame_ids(feature_name: str) -> list[str]:
        permission = get_permission(feature_name, ["frames"])

        if permission == "DISABLED":
            return []

        return list(
            get_dict(
                ParamDataHandler.select_data(feature_name, "ROOT"), ["frames"]
            ).keys()
        )

    @staticmethod
    def state_is_enable(feature_name: str) -> bool:
        root_state = get_dict(
            ParamDataHandler.select_data(feature_name, "ROOT"), ["state"]
        )

        return bool(root_state != "disable")

    @staticmethod
    def get_state(feature_name: str) -> dict:
        return get_dict(ParamDataHandler.select_data(feature_name, "USER"), ["state"])

    @staticmethod
    def save_params(feature_name: str):
        data = ParamDataHandler.__data_dict[feature_name]
        write_json(data.user_filepath, data.user)

    @staticmethod
    def get_value(path: str):
        feature_name, path_keys = break_path(path)

        if not is_value(path_keys):
            raise ParamException(path, "NODE")

        permission = get_permission(feature_name, path_keys)

        if permission == "DISABLED":
            return None
        if permission == "ROOT":
            return get_dict(
                ParamDataHandler.select_data(feature_name, "ROOT"), path_keys
            )
        if permission == "RESTRICTED":
            return (
                get_dict(ParamDataHandler.select_data(feature_name, "USER"), path_keys)
                or get_dict(
                    ParamDataHandler.select_data(feature_name, "ROOT"), path_keys
                )[0]
            )
        if permission == "USER":
            return get_dict(
                ParamDataHandler.select_data(feature_name, "USER"), path_keys
            )

    @staticmethod
    def set_value(path: str, value: Any) -> None:
        feature_name, path_keys = break_path(path)

        if not is_value(path_keys):
            raise ParamException(path, "NODE")

        permission = get_permission(feature_name, path_keys)

        if permission in ["DISABLED", "ROOT"]:
            raise ParamException(path, permission)

        if permission == "RESTRICTED":
            if not value in get_dict(
                ParamDataHandler.select_data(feature_name, "ROOT"), path_keys
            ):
                raise ParamException(path, permission)

        user_dict = copy.deepcopy(ParamDataHandler.__data_dict[feature_name].user)
        set_dict(user_dict, path_keys, value)

        try:
            ParamDataHandler.__data_dict[feature_name].user = user_FeatureParams(
                **user_dict
            ).model_dump(exclude_none=True)

            if path in ParamDataHandler.__listeners:
                param_listeners = ParamDataHandler.__listeners[path]

                for listener in param_listeners:
                    listener(value)

        except ValidationError as validation_error:
            raise ParamsValidationError(
                title="Validation error",
                validation_error=validation_error,
            )
