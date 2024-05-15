from pydantic import BaseModel, ConfigDict, ValidationError
from .ParamsBuilder import ParamsBuilder
from .ParamsError import ParamsValidationError
from ..models import FrameParams, root_FeatureParams_dict


class FeatureParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_filepath: str
    dev_mode: bool | None = None

    autostart: bool | None = None
    frames: dict[str, FrameParams] | None = None
    state: dict | None = None

    @staticmethod
    def create(
        root_params_dict: root_FeatureParams_dict,
        user_filepath: str,
        dev_mode: bool = False,
    ):
        params_builder = ParamsBuilder(root_params_dict, user_filepath)
        param_dict = params_builder.build()
        param_dict["dev_mode"] = dev_mode

        try:
            return FeatureParams(**param_dict)
        except ValidationError as validation_error:
            raise ParamsValidationError(
                title="Validation error", validation_error=validation_error
            )
