from pydantic import ValidationError
from typing import Callable, Any
from .RootBuilder import RootBuilder
from .ParamsError import ParamsValidationError
from ..utils import read_json
from ..models import (
    root_FeatureParams_dict,
    user_FeatureParams_dict,
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

        self.param_listeners: dict[str, list[Callable[[str, Any], None]]] = {}
