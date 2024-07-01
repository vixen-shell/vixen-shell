from typing import Any
from pydantic import BaseModel, ConfigDict, ValidationError
from .RootBuilder import RootBuilder
from .ParamsError import ParamsValidationError

from ..models import (
    FrameParams,
    root_FeatureParams_dict,
    root_FeatureParams,
    user_FeatureParams,
)

from ..utils import read_json, write_json


class FeatureParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    root: root_FeatureParams
    user: user_FeatureParams

    user_filepath: str
    dev_mode: bool | None = None

    autostart: bool | None = None
    frames: dict[str, FrameParams] | None = None
    state: dict | None = None

    @staticmethod
    def create(
        root_params_dict: root_FeatureParams_dict,
        user_params_filepath: str,
        dev_mode: bool = False,
    ):
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

        param_dict, new_root_params_dict = params_builder.build()

        param_dict["root"] = new_root_params_dict
        param_dict["user"] = user_params
        param_dict["user_filepath"] = user_params_filepath
        param_dict["dev_mode"] = dev_mode

        try:
            return FeatureParams(**param_dict)
        except ValidationError as validation_error:
            raise ParamsValidationError(
                title="Validation error", validation_error=validation_error
            )

    def model_post_init(self, __context: Any) -> None:
        if self.state_is_enable:
            if self.state == None:
                self.state = {}

    @property
    def state_is_enable(self) -> bool:
        return bool(self.root.state != "disable")

    def save_state(self):
        self.user.state = self.state

        write_json(
            self.user_filepath,
            self.user.model_dump(exclude_none=True),
        )
