from .ParamsError import ParamsError, ParamsErrorDetails

from ..models import (
    FeatureParams_dict,
    root_FeatureParams,
    root_FeatureParams_dict,
    root_FrameParams_dict,
    root_LayerFrameParams_dict,
    root_MarginParams_dict,
    user_FeatureParams,
    user_FeatureParams_dict,
    user_FrameParams,
)


class ParamsBuilder:
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
        self._params_dict = self.__init_params_dict(
            user_params.model_dump(exclude_none=True)
        )

    def __init_params_dict(
        self, user_params_dict: user_FeatureParams_dict
    ) -> FeatureParams_dict:
        root_frames = self._root_params_dict.get("frames")
        root_templates = self._root_params_dict.get("templates")
        user_frames = user_params_dict.get("frames")

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

                    del user_params_dict["frames"][key]["template"]

        params_dict: FeatureParams_dict = user_params_dict
        return params_dict

    def handle_param(self, path: tuple[str], callback=None):
        def get_value(_dict: dict):
            for key in path:
                try:
                    _dict = _dict[key]
                except KeyError:
                    return None
            return _dict

        def set_param_value(value):
            _dict = self._params_dict

            for key in path[:-1]:
                _dict = _dict.setdefault(key, {})
            _dict[path[-1]] = value

        root_value = get_value(self._root_params_dict)
        user_value = get_value(self._params_dict)

        if root_value is not None:

            if root_value == "disable":
                if user_value is not None:
                    raise ParamsError(
                        title=f"Validation error in '{self._user_params_filepath}'",
                        message="Field disabled by root parameters",
                        details=ParamsErrorDetails(loc=path),
                    )

                set_param_value(None)

            else:
                if not callback:

                    if user_value is not None:
                        raise ParamsError(
                            title=f"Validation error in '{self._user_params_filepath}'",
                            message="Field already defined in root parameters",
                            details=ParamsErrorDetails(loc=path),
                        )

                    set_param_value(root_value)

                else:
                    callback()

    def build(self) -> FeatureParams_dict:
        def handle_frames():
            for key, frame in self._root_params_dict["frames"].items():
                self.__build_frame(key, frame)

        self.handle_param(("frames",), handle_frames)
        self.handle_param(("autostart",))
        self.handle_param(("state",))

        return self._params_dict

    def __build_frame(self, frame_key: str, frame: root_FrameParams_dict):
        self.handle_param(("frames", frame_key, "name"))
        self.handle_param(("frames", frame_key, "route"))
        self.handle_param(("frames", frame_key, "show_on_startup"))

        self.handle_param(
            ("frames", frame_key, "layer_frame"),
            lambda: self.__build_layer_frame(frame_key, frame["layer_frame"]),
        )

    def __build_layer_frame(
        self, frame_key: str, layer_frame: root_LayerFrameParams_dict
    ):
        for key in layer_frame.keys():
            if key == "margins":
                self.handle_param(
                    ("frames", frame_key, "layer_frame", "margins"),
                    lambda: self.__build_layer_frame_margins(
                        frame_key, layer_frame["margins"]
                    ),
                )
            else:
                self.handle_param(("frames", frame_key, "layer_frame", key))

    def __build_layer_frame_margins(
        self, frame_key: str, layer_frame_margins: root_MarginParams_dict
    ):
        for key in layer_frame_margins.keys():
            self.handle_param(("frames", frame_key, "layer_frame", "margins", key))


# class _ParamsBuilder:
#     def __init__(
#         self,
#         root_params: root_FeatureParams,
#         user_params: user_FeatureParams,
#         user_params_filepath: str,
#     ):
#         self._root_params = root_params
#         self._user_params = user_params

#         self._user_params_filepath = user_params_filepath
#         self.__templates_postprocess()

#         self._params_dict: FeatureParams_dict = self._user_params.model_dump(
#             exclude_none=True
#         )

#     def __templates_postprocess(self):
#         if self._user_params.frames:
#             if not self._root_params.frames and not self._root_params.templates:
#                 raise ParamsError(
#                     title=f"Validation error in '{self._user_params_filepath}'",
#                     message="Cannot contain 'frames' fields on this feature",
#                     details=ParamsErrorDetails(loc=("frames",)),
#                 )

#             valid_frame_keys = []
#             if self._root_params.frames:
#                 valid_frame_keys = list(self._root_params.frames.keys())

#             valid_template_keys = []
#             if self._root_params.templates:
#                 valid_template_keys = list(self._root_params.templates.keys())

#             for key, frame in self._user_params.frames.items():
#                 if not key in valid_frame_keys:

#                     if not frame.template:
#                         raise ParamsError(
#                             title=f"Missing parameters in '{self._user_params_filepath}'",
#                             message="A custom frame must reference a frame template to be valid",
#                             details=ParamsErrorDetails(
#                                 loc=("frames", key, "template"), value="Missing"
#                             ),
#                         )

#                     if not frame.template in valid_template_keys:
#                         raise ParamsError(
#                             title=f"Validation error in '{self._user_params_filepath}'",
#                             message=f"The '{frame.template}' frame template does not exist in the root parameters",
#                             details=ParamsErrorDetails(
#                                 loc=("frames", key, "template"), value=frame.template
#                             ),
#                         )

#                     self._root_params.frames[key] = self._root_params.templates[
#                         frame.template
#                     ]

#                     self._user_params.frames[key] = user_FrameParams(
#                         **frame.model_dump(exclude="template")
#                     )

#     def __param_validator(self, root_value):
#         if root_value is not None:
#             if root_value != "disable":
#                 return root_value
#             else:
#                 return None
#         else:
#             return "__user__"

#     def build(self) -> FeatureParams_dict:
#         self._params_dict["user_filepath"] = self._user_params_filepath

#         autostart = self.__param_validator(self._root_params.autostart)
#         if autostart != "__user__":
#             self._params_dict["autostart"] = autostart

#         if self._root_params.frames:
#             if not "frames" in self._params_dict:
#                 self._params_dict["frames"] = {}

#             for key, frame in self._root_params.frames.items():
#                 self.__build_frame(key, frame.model_dump())

#         state = self.__param_validator(self._root_params.state)
#         if state != "__user__":
#             self._params_dict["state"] = state

#         return self._params_dict

#     def __build_frame(self, frame_key: str, frame: root_FrameParams_dict):
#         if not self._params_dict["frames"].get(frame_key):
#             self._params_dict["frames"][frame_key] = {}

#         self._params_dict["frames"][frame_key]["name"] = frame["name"]
#         self._params_dict["frames"][frame_key]["route"] = frame["route"]

#         show_on_startup = self.__param_validator(frame["show_on_startup"])
#         if show_on_startup != "__user__":
#             self._params_dict["frames"][frame_key]["show_on_startup"] = show_on_startup

#         layer_frame = self.__param_validator(frame["layer_frame"])
#         if layer_frame != "__user__":
#             if layer_frame is None:
#                 self._params_dict["frames"][frame_key]["layer_frame"] = layer_frame
#             else:
#                 self.__build_layer_frame(frame_key, frame["layer_frame"])

#     def __build_layer_frame(
#         self, frame_key: str, layer_frame: root_LayerFrameParams_dict
#     ):
#         if not self._params_dict["frames"][frame_key].get("layer_frame"):
#             self._params_dict["frames"][frame_key]["layer_frame"] = {}

#         for key, value in layer_frame.items():
#             if key == "margins":
#                 margins = self.__param_validator(value)
#                 if margins != "__user__":
#                     if margins is None:
#                         self._params_dict["frames"][frame_key]["layer_frame"][
#                             key
#                         ] = margins
#                     else:
#                         self.__build_layer_frame_margins(
#                             frame_key, layer_frame["margins"]
#                         )
#             else:
#                 root_value = self.__param_validator(value)
#                 if root_value != "__user__":
#                     self._params_dict["frames"][frame_key]["layer_frame"][
#                         key
#                     ] = root_value

#     def __build_layer_frame_margins(
#         self, frame_key: str, layer_frame_margins: root_MarginParams_dict
#     ):
#         if not self._params_dict["frames"][frame_key]["layer_frame"].get("margins"):
#             self._params_dict["frames"][frame_key]["layer_frame"]["margins"] = {}

#         for key, value in layer_frame_margins.items():
#             root_value = self.__param_validator(value)
#             if root_value != "__user__":
#                 self._params_dict["frames"][frame_key]["layer_frame"]["margins"][
#                     key
#                 ] = value
