import copy
from typing import Literal, Any, Callable
from pydantic import ValidationError
from ..classes import ParamData, ParamsValidationError, ParamPermissionError
from ..utils import write_json
from vx_types import (
    root_FeatureParams_dict,
    user_FeatureParams_dict,
    user_FeatureParams,
    ParamPermission,
)


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


def get_permission(feature_name: str, path_keys: list[str]) -> ParamPermission:
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

    @staticmethod
    def add_param_data(feature_name: str, param_data: ParamData):
        ParamDataHandler.__data_dict[feature_name] = param_data

    @staticmethod
    def remove_param_data(feature_name: str):
        if feature_name in ParamDataHandler.__data_dict:
            ParamDataHandler.__data_dict.pop(feature_name)

    @staticmethod
    def add_param_listener(path: str, listener: Callable[[str, Any], None]):
        feature_name, _ = break_path(path)
        param_listeners = ParamDataHandler.__data_dict[feature_name].param_listeners
        listeners = param_listeners.get(path)

        if listeners:
            listeners.append(listener)
        else:
            param_listeners[path] = [listener]

    @staticmethod
    def remove_param_listener(path: str, listener: Callable[[str, Any], None]):
        feature_name, _ = break_path(path)
        param_listeners = ParamDataHandler.__data_dict[feature_name].param_listeners
        listeners = param_listeners.get(path)

        if listeners:
            listeners.remove(listener)

            if len(listeners) == 0:
                param_listeners.pop(path)

    @staticmethod
    def select_data(
        feature_name: str, type: Literal["ROOT", "USER"]
    ) -> root_FeatureParams_dict | user_FeatureParams_dict:
        return getattr(ParamDataHandler.__data_dict[feature_name], type.lower())

    @staticmethod
    def node_is_define(path: str) -> bool:
        feature_name, path_keys = break_path(path)

        if is_value(path_keys):
            raise ParamPermissionError(path, "VALUE")

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
    def save_params(feature_name: str):
        data = ParamDataHandler.__data_dict[feature_name]
        write_json(data.user_filepath, data.user)

    @staticmethod
    def get_value(path: str) -> Any | None:
        feature_name, path_keys = break_path(path)

        if not is_value(path_keys):
            raise ParamPermissionError(path, "NODE")

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
            raise ParamPermissionError(path, "NODE")

        permission = get_permission(feature_name, path_keys)

        if permission in ["DISABLED", "ROOT"]:
            raise ParamPermissionError(path, permission)

        if permission == "RESTRICTED":
            if not value in get_dict(
                ParamDataHandler.select_data(feature_name, "ROOT"), path_keys
            ):
                raise ParamPermissionError(path, permission)

        user_dict = copy.deepcopy(ParamDataHandler.__data_dict[feature_name].user)
        set_dict(user_dict, path_keys, value)

        try:
            ParamDataHandler.__data_dict[feature_name].user = user_FeatureParams(
                **user_dict
            ).model_dump(exclude_none=True)

            ParamDataHandler.__handle_listeners(path, value)

        except ValidationError as validation_error:
            raise ParamsValidationError(
                title="Validation error",
                validation_error=validation_error,
            )

    @staticmethod
    def __handle_listeners(path: str, value: Any):
        feature_name, _ = break_path(path)
        param_listeners = ParamDataHandler.__data_dict[feature_name].param_listeners

        for key in param_listeners.keys():
            if path.startswith(key):
                listeners = param_listeners[key]

                for listener in listeners:
                    listener(path, value)
