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
    def create(file_name: str):
        builder = ParmetersBuilder(file_name)
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
