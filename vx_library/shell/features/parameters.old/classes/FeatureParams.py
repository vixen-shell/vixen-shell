from typing import Optional, Dict
from pydantic import BaseModel, ConfigDict

# from vx_feature_utils import RootFeatureParamsDict
from .ParamsBuilder import ParamsBuilder
from ..models import FrameParams
from ..utils import write_json


class FeatureParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    start: Optional[bool] = None
    frames: Dict[str, FrameParams]
    state: Optional[Dict[str, None | str | int | float | bool]] = None
    dev: Optional[bool] = False

    @staticmethod
    def create(root_dict, user_file_path: str, dev: bool = False):
        builder = ParamsBuilder(root_dict, user_file_path)

        params_dict = builder.build()
        params_dict["dev"] = dev
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
