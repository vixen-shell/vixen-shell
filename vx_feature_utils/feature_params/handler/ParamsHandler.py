from dataclasses import dataclass
from typing import Literal, TypeVar, Generic
from pydantic import ValidationError
from ..classes import (
    FeatureParams,
    ParamsValidationError,
)
from ..models import (
    root_FeatureParams_dict,
    user_FeatureParams_dict,
    user_FeatureParams,
    LevelKeys,
    AnchorEdgeKeys,
    AlignmentKeys,
)


@dataclass
class ParamData:
    root: root_FeatureParams_dict
    user: user_FeatureParams_dict


def get_dict_value(inspect: dict, path: str):
    node = inspect
    keys = path.split(".")

    for key in keys:
        try:
            node = node[key]
        except KeyError:
            return None
    return node


def set_dict_value(inspect: dict, path: str, value):
    node = inspect
    keys = path.split(".")

    for key in keys[:-1]:
        node = node.setdefault(key, {})
    node[keys[-1]] = value


class SetParamException(Exception):
    def __init__(self, param_type: Literal["DISABLED", "ROOT", "RESTRICTED"]) -> None:
        if param_type == "DISABLED":
            message = "Disabled parameter, cannot define user value"
        if param_type == "ROOT":
            message = "Root definition, cannot define user value"
        if param_type == "RESTRICTED":
            message = f"Root definition, bad user value"

        super().__init__(message)
        self.param_type = param_type


T = TypeVar("T", bool, int, str, dict, LevelKeys, AnchorEdgeKeys, AlignmentKeys)


class Param(Generic[T]):
    def __init__(
        self,
        path: str,
        param_data: ParamData,
    ):
        if get_dict_value(user_FeatureParams_dict.get_structure(), path) != "VALUE":
            raise Exception("The specified path does not return a value but a node")

        self._path = path
        self._data = param_data

    @property
    def state(self) -> Literal["DISABLED", "ROOT", "RESTRICTED", "USER"]:
        root_value = get_dict_value(self._data.root, self._path)

        if root_value is None:
            return "USER"
        if root_value == "disable":
            return "DISABLED"
        if isinstance(root_value, list):
            return "RESTRICTED"

        return "ROOT"

    @property
    def value(self) -> T | None:
        state = self.state

        if state == "DISABLED":
            return None
        if state == "ROOT":
            return get_dict_value(self._data.root, self._path)
        if state == "RESTRICTED":
            return get_dict_value(self._data.user, self._path) or get_dict_value(
                self._data.root, self._path
            )
        if state == "USER":
            return get_dict_value(self._data.user, self._path)

    @value.setter
    def value(self, value: T | None):
        state = self.state

        if state in ["DISABLED", "ROOT"]:
            raise SetParamException(state)

        if state == "RESTRICTED":
            if not value in get_dict_value(self._data.root, self._path):
                raise SetParamException(state)

        user_dict = self._data.user.copy()
        set_dict_value(user_dict, self._path, value)

        try:
            self._data.user = user_FeatureParams(**user_dict).model_dump(
                exclude_none=True
            )
        except ValidationError as validation_error:
            raise ParamsValidationError(
                title="Validation error",
                validation_error=validation_error,
            )


class MarginParamsHandler:
    def __init__(self, param_data: ParamData, frame_id: str) -> None:
        self.top = Param[int](f"frames.{frame_id}.layer_frame.margins.top", param_data)
        self.right = Param[int](
            f"frames.{frame_id}.layer_frame.margins.right", param_data
        )
        self.bottom = Param[int](
            f"frames.{frame_id}.layer_frame.margins.bottom", param_data
        )
        self.left = Param[int](
            f"frames.{frame_id}.layer_frame.margins.left", param_data
        )


class LayerFrameParamsHandler:
    def __init__(self, param_data: ParamData, frame_id: str) -> None:
        self.monitor_id = Param[int](
            f"frames.{frame_id}.layer_frame.monitor_id", param_data
        )
        self.auto_exclusive_zone = Param[bool](
            f"frames.{frame_id}.layer_frame.auto_exclusive_zone", param_data
        )
        self.exclusive_zone = Param[int](
            f"frames.{frame_id}.layer_frame.exclusive_zone", param_data
        )
        self.level = Param[LevelKeys](
            f"frames.{frame_id}.layer_frame.level", param_data
        )
        self.anchor_edge = Param[AnchorEdgeKeys](
            f"frames.{frame_id}.layer_frame.anchor_edge", param_data
        )
        self.alignment = Param[AlignmentKeys](
            f"frames.{frame_id}.layer_frame.alignment", param_data
        )
        self.margins = MarginParamsHandler(param_data, frame_id)
        self.width = Param[int](f"frames.{frame_id}.layer_frame.width", param_data)
        self.height = Param[int](f"frames.{frame_id}.layer_frame.height", param_data)


class FrameParamsHandler:
    def __init__(self, param_data: ParamData, frame_id: str) -> None:
        self.name: str = get_dict_value(param_data.root, f"frames.{frame_id}.name")
        self.route: str = get_dict_value(param_data.root, f"frames.{frame_id}.route")
        self.show_on_startup = Param[bool](
            f"frames.{frame_id}.show_on_startup", param_data
        )
        self.layer_frame = LayerFrameParamsHandler(param_data, frame_id)


class ParamsHandler:
    def __init__(self, feature_params: FeatureParams) -> None:
        self._param_data = ParamData(
            root=feature_params.root.model_dump(exclude_none=True),
            user=feature_params.user.model_dump(exclude_none=True),
        )

        self.user_filepath = feature_params.user_filepath
        self.dev_mode = feature_params.dev_mode

        self.autostart = Param[bool]("autostart", self._param_data)
        self.frames: dict[str, FrameParamsHandler] = {}

        root_frames = self._param_data.root.get("frames")
        if root_frames and root_frames != "disable":
            for key in root_frames.keys():
                self.frames[key] = FrameParamsHandler(self._param_data, key)

        self.state = Param("state", self._param_data)
