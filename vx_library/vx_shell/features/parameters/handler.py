import os, json
from typing import Literal, Optional, Dict, Any
from pydantic import BaseModel, validator
from .models import RootFeatureParams, RootFeatureParamsDict
from .models import UserFeatureParams, UserFeatureParamsDict
from .models import LayerFrameParamsDict
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


class FeatureParamsFactory:
    def __init__(self, file_name: str):
        root: RootFeatureParamsDict = RootFeatureParams(
            **read_json(f"{ROOT_PARAMS_DIRECTORY}/{file_name}")
        ).model_dump()

        user: UserFeatureParamsDict = UserFeatureParams(
            read_json(f"{USER_PARAMS_DIRECTORY}/{file_name}")
        ).model_dump()

        self.path: str = f"{USER_PARAMS_DIRECTORY}/{file_name}"
        self.name: str = root["name"]
        self.frames: LayerFrameParamsDict = user["frames"] or {}

        root_frames = root["frames"]
        for key, frame in root_frames.items():
            if not key in self.frames:
                self.frames[key] = {}

        state = root.get("state")
        if state:
            self.state = None if state == "disable" else state
