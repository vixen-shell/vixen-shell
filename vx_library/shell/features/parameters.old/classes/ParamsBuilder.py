from typing import Any, Literal
from pydantic import ValidationError
from ..utils import read_json

from ..models import (
    RootFeatureParams,
    RootFeatureParamsDict,
    RootFrameParamsDict,
    RootLayerFrameParamsDict,
    RootMarginParamsDict,
    UserFeatureParams,
    UserFeatureParamsDict,
    FeatureParamsDict,
)


class ParameterError(Exception):
    def __init__(self, file_path: str, validation_error: ValidationError):
        error = validation_error.errors()[0]

        super().__init__(
            f"{error['msg']}: {error['type']} {list(error['loc'])} on '{file_path}' configuration file"
        )


class ParamsBuilder:
    def __init__(self, root_dict: RootFeatureParamsDict, user_file_path: str):
        self.user_file_path = user_file_path

        self.root_data: RootFeatureParamsDict = RootFeatureParams(
            **root_dict
        ).model_dump()

        try:
            self.data: FeatureParamsDict = self.init_data(
                UserFeatureParams(**read_json(user_file_path) or {}).model_dump()
            )
        except ValidationError as error:
            raise ParameterError(user_file_path, error)

    def init_data(self, user_data: UserFeatureParamsDict):
        if self.root_data.get("templates"):
            root_frame_keys = list(self.root_data["frames"].keys())
            root_template_keys = list(self.root_data["templates"].keys())

            for key in user_data["frames"]:
                if not key in root_frame_keys:
                    template_key = user_data["frames"][key].get("template")

                    if template_key and template_key in root_template_keys:
                        self.root_data["frames"][key] = self.root_data["templates"][
                            template_key
                        ]

        return user_data

    def root_validator(self, root_value: Any | Literal["disable"] | None):
        if root_value is not None:
            if root_value != "disable":
                return root_value
            else:
                return None
        else:
            return "__user__"

    def build(self):
        self.data["path"] = self.user_file_path

        start = self.root_validator(self.root_data["start"])
        if start != "__user__":
            self.data["start"] = start

        if not "frames" in self.data:
            self.data["frames"] = {}

        for frame_key, root_frame in self.root_data["frames"].items():
            self.build_frame_data(frame_key, root_frame)

        state = self.root_validator(self.root_data["state"])
        if state != "__user__":
            self.data["state"] = state

        return self.data

    def build_frame_data(self, frame_key: str, root_frame: RootFrameParamsDict):
        if not frame_key in self.data["frames"]:
            self.data["frames"][frame_key] = {}

        self.data["frames"][frame_key]["name"] = root_frame["name"]
        self.data["frames"][frame_key]["route"] = root_frame["route"]

        show_on_startup = self.root_validator(root_frame["show_on_startup"])
        if show_on_startup != "__user__":
            self.data["frames"][frame_key]["show_on_startup"] = show_on_startup

        layer_frame = self.root_validator(root_frame["layer_frame"])
        if layer_frame != "__user__":
            if layer_frame is None:
                self.data["frames"][frame_key]["layer_frame"] = layer_frame
            else:
                self.build_layer_frame_data(frame_key, root_frame["layer_frame"])

    def build_layer_frame_data(
        self, frame_key: str, root_layer_frame: RootLayerFrameParamsDict
    ):
        if not self.data["frames"][frame_key].get("layer_frame"):
            self.data["frames"][frame_key]["layer_frame"] = {}

        for key, value in root_layer_frame.items():
            if key == "margins":
                margins = self.root_validator(value)
                if margins != "__user__":
                    if margins is None:
                        self.data["frames"][frame_key]["layer_frame"][key] = margins
                    else:
                        self.build_margins_data(frame_key, root_layer_frame["margins"])
            else:
                root_value = self.root_validator(value)
                if root_value != "__user__":
                    self.data["frames"][frame_key]["layer_frame"][key] = root_value

    def build_margins_data(self, frame_key: str, root_margins: RootMarginParamsDict):
        if not self.data["frames"][frame_key]["layer_frame"].get("margins"):
            self.data["frames"][frame_key]["layer_frame"]["margins"] = {}

        for key, value in root_margins.items():
            root_value = self.root_validator(value)
            if root_value != "__user__":
                self.data["frames"][frame_key]["layer_frame"]["margins"][key] = value
