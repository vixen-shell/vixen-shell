from typing import Optional, Dict
from pydantic import BaseModel
from .models import FrameParams
from .builder import ParmetersBuilder
from .utils import write_json


class FeatureParams(BaseModel):
    path: str
    name: str
    frames: Dict[str, FrameParams]
    state: Optional[Dict[str, None | str | int | float | bool]] = None

    @staticmethod
    def create(root_file_path: str, user_file_path: str):
        builder = ParmetersBuilder(root_file_path, user_file_path)
        return FeatureParams(**builder.build())

    def save(self):
        frames = {}

        for key in self.frames:
            frames[key] = self.frames[key].model_dump(
                exclude={"name", "route"}, exclude_none=True
            )

        data = self.model_dump(exclude={"path", "name", "frames"})
        data["frames"] = frames

        write_json(self.path, data)
