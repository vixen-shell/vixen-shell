import copy
from typing import Literal, Any, Callable
from pydantic import ValidationError
from ..classes import ParamData, ParamsValidationError, ParamPermissionError
from ..utils import write_json
from ..models import (
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
    __param_listeners: dict[str, list[Callable[[Any], None]]] = {}
    __layer_frame_param_listeners: dict[str, list[Callable[[Any], None]]] = {}

    @staticmethod
    def add_param_data(feature_name: str, param_data: ParamData):
        ParamDataHandler.__data_dict[feature_name] = param_data

    @staticmethod
    def remove_param_data(feature_name: str):
        ParamDataHandler.__data_dict.pop(feature_name)

    @staticmethod
    def add_param_listener(path: str, listener: Callable[[Any], None]):
        path_listeners = ParamDataHandler.__param_listeners.get(path)

        if path_listeners:
            path_listeners.append(listener)
        else:
            ParamDataHandler.__param_listeners[path] = [listener]

    @staticmethod
    def add_layer_frame_param_listener(
        feature_name: str, frame_id: str, listener: Callable[[Any], None]
    ):
        frame_path = f"{feature_name}.frames.{frame_id}.layer_frame"
        path_listeners = ParamDataHandler.__layer_frame_param_listeners.get(frame_path)

        if path_listeners:
            path_listeners.append(listener)
        else:
            ParamDataHandler.__layer_frame_param_listeners[frame_path] = [listener]

    @staticmethod
    def remove_param_listener(path: str, listener: Callable[[Any], None]):
        path_listeners = ParamDataHandler.__param_listeners.get(path)

        if path_listeners:
            path_listeners.remove(listener)

            if len(path_listeners) == 0:
                ParamDataHandler.__param_listeners.pop(path)

    @staticmethod
    def remove_layer_frame_param_listener(
        feature_name: str, frame_id: str, listener: Callable[[Any], None]
    ):
        frame_path = f"{feature_name}.frames.{frame_id}.layer_frame"
        path_listeners = ParamDataHandler.__layer_frame_param_listeners.get(frame_path)

        if path_listeners:
            path_listeners.remove(listener)

            if len(path_listeners) == 0:
                ParamDataHandler.__layer_frame_param_listeners.pop(frame_path)

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

            if path in ParamDataHandler.__param_listeners:
                param_listeners = ParamDataHandler.__param_listeners[path]

                for listener in param_listeners:
                    listener(value)

            for key in ParamDataHandler.__layer_frame_param_listeners.keys():
                if path.startswith(key):
                    layer_frame_param_listeners = (
                        ParamDataHandler.__layer_frame_param_listeners[key]
                    )

                    for listener in layer_frame_param_listeners:
                        listener(value)

        except ValidationError as validation_error:
            raise ParamsValidationError(
                title="Validation error",
                validation_error=validation_error,
            )
