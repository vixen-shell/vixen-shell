import os, json
from typing import Literal, Optional, Dict, Any
from pydantic import BaseModel
from .models import RootFeatureParams, UserFeatureParams, FrameParams
from .builder import ParmetersBuilder
from ...globals import ROOT_CONFIG_DIRECTORY, USER_CONFIG_DIRECTORY

ROOT_PARAMS_DIRECTORY = f"{ROOT_CONFIG_DIRECTORY}/features"
USER_PARAMS_DIRECTORY = f"{USER_CONFIG_DIRECTORY}/features"


def read_json(file_path: str) -> dict | None:
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)


def write_json(file_path: str, data: dict):
    if os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    else:
        with open(file_path, "x", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)


class FeatureParams(BaseModel):
    path: str
    name: str
    frames: Dict[str, FrameParams]
    state: Optional[Dict[str, None | str | int | float | bool]] = None

    @staticmethod
    def create(file_name: str):
        builder = ParmetersBuilder(file_name)
        return FeatureParams(**builder.build())

    # @staticmethod
    # def create(file_name: str) -> dict:
    #     def root_validator(root_value: Any | Literal["disable"] | None):
    #         if root_value is not None:
    #             if root_value != "disable":
    #                 return root_value
    #             else:
    #                 return None
    #         else:
    #             return "__user__"

    #     def build_feature_params(root_data: Dict, user_data: Dict):
    #         root_params = RootFeatureParams(**root_data).model_dump()
    #         params = UserFeatureParams(**user_data).model_dump()

    #         params["path"] = f"{USER_PARAMS_DIRECTORY}/{file_name}"
    #         params["name"] = root_params["name"]

    #         if not "frames" in params:
    #             params["frames"] = {}

    #         for root_frame_key, root_frame_item in root_params["frames"].items():
    #             if not root_frame_key in params["frames"]:
    #                 params["frames"][root_frame_key] = {}

    #             params["frames"][root_frame_key]["name"] = root_frame_item["name"]
    #             params["frames"][root_frame_key]["route"] = root_frame_item["route"]

    #             show_on_startup = root_validator(root_frame_item["show_on_startup"])
    #             if show_on_startup != "__user__":
    #                 params["frames"][root_frame_key][
    #                     "show_on_startup"
    #                 ] = show_on_startup

    #             layer_frame = root_validator(root_frame_item["layer_frame"])
    #             if layer_frame != "__user__":
    #                 if layer_frame is None:
    #                     params["frames"][root_frame_key]["layer_frame"] = None
    #                 else:
    #                     if not params["frames"][root_frame_key].get("layer_frame"):
    #                         params["frames"][root_frame_key]["layer_frame"] = {}

    #                     for layer_frame_key, layer_frame_item in root_frame_item[
    #                         "layer_frame"
    #                     ].items():
    #                         if layer_frame_key == "margins":
    #                             margins = root_validator(layer_frame_item)
    #                             if margins != "__user__":
    #                                 if margins is None:
    #                                     params["frames"][root_frame_key]["layer_frame"][
    #                                         layer_frame_key
    #                                     ] = None
    #                                 else:
    #                                     for margin_key, margin_item in root_frame_item[
    #                                         "layer_frame"
    #                                     ]["margins"].items():
    #                                         value = root_validator(margin_item)
    #                                         if value != "__user__":
    #                                             params["frames"][root_frame_key][
    #                                                 "layer_frame"
    #                                             ]["margins"][margin_key] = value
    #                         else:
    #                             value = root_validator(layer_frame_item)
    #                             if value != "__user__":
    #                                 params["frames"][root_frame_key]["layer_frame"][
    #                                     layer_frame_key
    #                                 ] = value

    #         state = root_validator(root_params["state"])
    #         if state != "__user__":
    #             params["state"] = state

    #         return params

    #     return FeatureParams(
    #         **build_feature_params(
    #             read_json(f"{ROOT_PARAMS_DIRECTORY}/{file_name}"),
    #             read_json(f"{USER_PARAMS_DIRECTORY}/{file_name}"),
    #         )
    #     )

    def save(self):
        frames = {}

        for key in self.frames:
            frames[key] = self.frames[key].model_dump(
                exclude={"name", "route"}, exclude_none=True
            )

        data = self.model_dump(exclude={"path", "name", "frames"})
        data["frames"] = frames

        write_json(self.path, data)
