from abc import ABC, abstractmethod
from vx_types import user_FrameParams_dict


class AbsFrames(ABC):
    @property
    @abstractmethod
    def ids(self) -> list[str]:
        pass

    @property
    @abstractmethod
    def actives(self) -> list[str]:
        pass

    @abstractmethod
    def open(self, id: str) -> str | None:
        pass

    @abstractmethod
    def close(self, id: str) -> None:
        pass

    @abstractmethod
    def new_from_template(self, id: str, frame_params: user_FrameParams_dict) -> bool:
        pass

    @abstractmethod
    def remove_from_template(self, id: str) -> bool:
        pass


def get_frames_reference(feature):
    class FeatureReference(AbsFrames):
        @property
        def ids(self) -> list[str]:
            return feature.frame_ids

        @property
        def actives(self) -> list[str]:
            return feature.active_frame_ids

        def open(self, id: str) -> str | None:
            return feature.open_frame(id)

        def close(self, id: str):
            return feature.close_frame(id)

        def new_from_template(
            self, id: str, frame_params: user_FrameParams_dict
        ) -> bool:
            return feature.new_frame_from_template(id, frame_params)

        def remove_from_template(self, id: str) -> bool:
            return feature.remove_frame_from_template(id)

    return FeatureReference()
