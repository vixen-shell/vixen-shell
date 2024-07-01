from .ParamsError import ParamsError, ParamsErrorDetails

from ..models import (
    root_FeatureParams,
    root_FeatureParams_dict,
    user_FeatureParams,
    user_FeatureParams_dict,
)


class RootBuilder:
    def __init__(
        self,
        root_params: root_FeatureParams,
        user_params: user_FeatureParams,
        user_params_filepath: str,
    ):
        self._user_params_filepath = user_params_filepath

        self._root_params_dict: root_FeatureParams_dict = root_params.model_dump(
            exclude_none=True
        )
        self._user_params_dict: user_FeatureParams_dict = user_params.model_dump(
            exclude_none=True
        )

    def build(self) -> root_FeatureParams_dict:
        root_frames = self._root_params_dict.get("frames")
        root_templates = self._root_params_dict.get("templates")
        user_frames = self._user_params_dict.get("frames")

        if user_frames is not None:
            if root_frames == "disable" or (not root_frames and not root_templates):
                raise ParamsError(
                    title=f"Validation error in '{self._user_params_filepath}'",
                    message="Cannot contain 'frames' fields on this feature",
                    details=ParamsErrorDetails(loc=("frames",)),
                )

            valid_frame_keys = list(root_frames.keys()) if root_frames else []
            valid_template_keys = list(root_templates.keys()) if root_templates else []

            for key, frame in user_frames.items():
                if not key in valid_frame_keys:

                    frame_template = frame.get("template")

                    if not frame_template:
                        raise ParamsError(
                            title=f"Missing parameters in '{self._user_params_filepath}'",
                            message="A custom frame must reference a frame template to be valid",
                            details=ParamsErrorDetails(
                                loc=("frames", key, "template"), value="Missing"
                            ),
                        )

                    if not frame_template in valid_template_keys:
                        raise ParamsError(
                            title=f"Validation error in '{self._user_params_filepath}'",
                            message=f"The '{frame_template}' frame template does not exist in the root parameters",
                            details=ParamsErrorDetails(
                                loc=("frames", key, "template"), value=frame_template
                            ),
                        )

                    self._root_params_dict["frames"][key] = self._root_params_dict[
                        "templates"
                    ][frame_template]

        return self._root_params_dict
