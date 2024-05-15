from pydantic import ValidationError

from .ParamsError import (
    ParamsValidationError,
    ParamsError,
    ParamsErrorDetails,
)
from ..models import (
    FeatureParams_dict,
    root_FeatureParams,
    root_FeatureParams_dict,
    root_FrameParams_dict,
    root_LayerFrameParams_dict,
    root_MarginParams_dict,
    user_FeatureParams,
    user_FrameParams,
)
from ...utils import read_json


class ParamsBuilder:
    def __init__(self, root_params_dict: root_FeatureParams_dict, user_filepath: str):
        try:
            self._root_params = root_FeatureParams(**root_params_dict)
        except ValidationError as validation_error:
            raise ParamsValidationError(
                title="Validation error in root parameters",
                validation_error=validation_error,
            )

        try:
            self._user_params = user_FeatureParams(**read_json(user_filepath) or {})
        except ValidationError as validation_error:
            raise ParamsValidationError(
                title=f"Validation error in '{user_filepath}'",
                validation_error=validation_error,
            )

        self._user_filepath = user_filepath
        self.__templates_postprocess()

        self._params_dict: FeatureParams_dict = self._user_params.model_dump(
            exclude_none=True
        )

    def __templates_postprocess(self):
        if self._user_params.frames:
            if not self._root_params.frames and not self._root_params.templates:
                raise ParamsError(
                    title=f"Validation error in '{self._user_filepath}'",
                    message="Cannot contain 'frames' fields on this feature",
                    details=ParamsErrorDetails(loc=("frames",)),
                )

            valid_frame_keys = []
            if self._root_params.frames:
                valid_frame_keys = list(self._root_params.frames.keys())

            valid_template_keys = []
            if self._root_params.templates:
                valid_template_keys = list(self._root_params.templates.keys())

            for key, frame in self._user_params.frames.items():
                if not key in valid_frame_keys:

                    if not frame.template:
                        raise ParamsError(
                            title=f"Missing parameters in '{self._user_filepath}'",
                            message="A custom frame must reference a frame template to be valid",
                            details=ParamsErrorDetails(
                                loc=("frames", key, "template"), value="Missing"
                            ),
                        )

                    if not frame.template in valid_template_keys:
                        raise ParamsError(
                            title=f"Validation error in '{self._user_filepath}'",
                            message=f"The '{frame.template}' frame template does not exist in the root parameters",
                            details=ParamsErrorDetails(
                                loc=("frames", key, "template"), value=frame.template
                            ),
                        )

                    self._root_params.frames[key] = self._root_params.templates[
                        frame.template
                    ]

                    self._user_params.frames[key] = user_FrameParams(
                        **frame.model_dump(exclude="template")
                    )

    def __param_validator(self, root_value):
        if root_value is not None:
            if root_value != "disable":
                return root_value
            else:
                return None
        else:
            return "__user__"

    def build(self) -> FeatureParams_dict:
        self._params_dict["user_filepath"] = self._user_filepath

        autostart = self.__param_validator(self._root_params.autostart)
        if autostart != "__user__":
            self._params_dict["autostart"] = autostart

        if self._root_params.frames:
            if not "frames" in self._params_dict:
                self._params_dict["frames"] = {}

            for key, frame in self._root_params.frames.items():
                self.__build_frame(key, frame.model_dump())

        state = self.__param_validator(self._root_params.state)
        if state != "__user__":
            self._params_dict["state"] = state

        return self._params_dict

    def __build_frame(self, frame_key: str, frame: root_FrameParams_dict):
        if not self._params_dict["frames"].get(frame_key):
            self._params_dict["frames"][frame_key] = {}

        self._params_dict["frames"][frame_key]["name"] = frame["name"]
        self._params_dict["frames"][frame_key]["route"] = frame["route"]

        show_on_startup = self.__param_validator(frame["show_on_startup"])
        if show_on_startup != "__user__":
            self._params_dict["frames"][frame_key]["show_on_startup"] = show_on_startup

        layer_frame = self.__param_validator(frame["layer_frame"])
        if layer_frame != "__user__":
            if layer_frame is None:
                self._params_dict["frames"][frame_key]["layer_frame"] = layer_frame
            else:
                self.__build_layer_frame(frame_key, frame["layer_frame"])

    def __build_layer_frame(
        self, frame_key: str, layer_frame: root_LayerFrameParams_dict
    ):
        if not self._params_dict["frames"][frame_key].get("layer_frame"):
            self._params_dict["frames"][frame_key]["layer_frame"] = {}

        for key, value in layer_frame.items():
            if key == "margins":
                margins = self.__param_validator(value)
                if margins != "__user__":
                    if margins is None:
                        self._params_dict["frames"][frame_key]["layer_frame"][
                            key
                        ] = margins
                    else:
                        self.__build_layer_frame_margins(
                            frame_key, layer_frame["margins"]
                        )
            else:
                root_value = self.__param_validator(value)
                if root_value != "__user__":
                    self._params_dict["frames"][frame_key]["layer_frame"][
                        key
                    ] = root_value

    def __build_layer_frame_margins(
        self, frame_key: str, layer_frame_margins: root_MarginParams_dict
    ):
        if not self._params_dict["frames"][frame_key]["layer_frame"].get("margins"):
            self._params_dict["frames"][frame_key]["layer_frame"]["margins"] = {}

        for key, value in layer_frame_margins.items():
            root_value = self.__param_validator(value)
            if root_value != "__user__":
                self._params_dict["frames"][frame_key]["layer_frame"]["margins"][
                    key
                ] = value
