import copy
from pydantic import ValidationError
from typing import Callable, Any
from .RootBuilder import RootBuilder
from .ParamsError import ParamsValidationError, ParamsValueError, ParamsErrorDetails
from ..utils import read_json
from vx_types import (
    root_FeatureParams_dict,
    user_FeatureParams_dict,
    user_FrameParams_dict,
    root_FeatureParams,
    user_FeatureParams,
)


class ParamData:
    def __init__(
        self,
        root_params_dict: root_FeatureParams_dict,
        user_params_filepath: str,
        dev_mode: bool = False,
    ) -> None:
        self.root: root_FeatureParams_dict = None
        self.user: user_FeatureParams_dict = None
        self.user_filepath: str = user_params_filepath
        self.param_listeners: dict[str, list[Callable[[str, Any], None]]] = {}
        self.dev_mode: bool = dev_mode

        self.build_params(root_params_dict, read_json(user_params_filepath) or {})

    def build_params(
        self,
        root_params_dict: root_FeatureParams_dict,
        user_params_dict: user_FeatureParams_dict,
        rebuild: bool = False,
    ):
        try:
            root_params = root_FeatureParams(**root_params_dict)
        except ValidationError as validation_error:
            raise ParamsValidationError(
                title="Validation error in root parameters",
                validation_error=validation_error,
            )

        try:
            user_params = user_FeatureParams(**user_params_dict)
        except ValidationError as validation_error:
            raise ParamsValidationError(
                title="Validation error in user parameters",
                validation_error=validation_error,
            )

        params_builder = RootBuilder(
            root_params.model_copy(),
            user_params.model_copy(),
            "[user parameters]" if rebuild else self.user_filepath,
        )

        self.root = params_builder.build()
        self.user = user_params.model_dump(exclude_none=True)

    def create_frame_from_template(
        self, frame_id: str, frame_params_dict: user_FrameParams_dict
    ):
        if self.root["frames"] == "disable":
            raise PermissionError("Frame creation for this feature is disabled")

        if frame_id in self.root["frames"]:
            raise ValueError(f"Frame ID '{frame_id}' already exists")

        template_name = frame_params_dict.get("template")
        if not template_name:
            raise ParamsValueError(
                title="Validation error in frame parameters",
                message="You must fill in the 'template' field",
                details=ParamsErrorDetails(loc=("template",)),
            )

        user_dict: user_FeatureParams_dict = copy.deepcopy(self.user)

        if not user_dict.get("frames"):
            user_dict["frames"] = {}

        user_dict["frames"][frame_id] = frame_params_dict

        try:
            self.user = user_FeatureParams(**user_dict).model_dump(exclude_none=True)

        except ValidationError as validation_error:
            raise ParamsValidationError(
                title="Validation error",
                validation_error=validation_error,
            )

        self.build_params(self.root, self.user, True)

    def remove_frame_from_template(self, frame_id: str):
        if self.root["frames"] == "disable":
            raise PermissionError("Frame creation for this feature is disabled")

        if not self.user.get("frames") or not frame_id in self.user["frames"]:
            raise ValueError(f"Frame ID '{frame_id}' not exists")

        template_name = self.user["frames"][frame_id].get("template")
        if not template_name:
            raise ValueError(f"Frame '{frame_id}' is not defined on a template")

        root_dict: root_FeatureParams_dict = copy.deepcopy(self.root)
        user_dict: user_FeatureParams_dict = copy.deepcopy(self.user)

        root_dict["frames"].pop(frame_id)
        user_dict["frames"].pop(frame_id)

        if not user_dict["frames"].keys():
            user_dict.pop("frames")

        try:
            self.root = root_FeatureParams(**root_dict).model_dump(exclude_none=True)
            self.user = user_FeatureParams(**user_dict).model_dump(exclude_none=True)

        except ValidationError as validation_error:
            raise ParamsValidationError(
                title="Validation error",
                validation_error=validation_error,
            )

        self.build_params(self.root, self.user, True)
