from typing import Optional, Dict
from pydantic import BaseModel, ConfigDict

from .ParamsBuilder import ParamsBuilder
from ..models import (
    FrameParams,
    RootFeatureParamsDict,
    UserFeatureParamsDict,
    RootFeatureParams,
    UserFeatureParams,
)
from ...utils import read_json, write_json


class FeatureParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    start: Optional[bool] = None
    frames: Optional[Dict[str, FrameParams]] = {}
    state: Optional[Dict[str, None | str | int | float | bool]] = None
    dev: Optional[bool] = False

    @staticmethod
    def create(
        root_params_dict: RootFeatureParamsDict,
        user_params_filepath: str,
        dev_mode: bool = False,
    ):
        root_data: RootFeatureParamsDict = RootFeatureParams(
            **root_params_dict
        ).model_dump()

        user_data: UserFeatureParamsDict = UserFeatureParams(
            **read_json(user_params_filepath) or {}
        ).model_dump()

        builder = ParamsBuilder(root_data, user_data)

        params_dict = builder.build()
        params_dict["path"] = user_params_filepath
        params_dict["dev"] = dev_mode

        return FeatureParams(**params_dict)

    def save(self):
        frames = {}

        for key in self.frames:
            frames[key] = self.frames[key].model_dump(
                exclude={"name", "route"}, exclude_none=True
            )

        data = self.model_dump(exclude={"path", "name", "frames"})
        data["frames"] = frames

        write_json(self.path, data)
