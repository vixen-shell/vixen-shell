from abc import ABC, abstractmethod


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
    def open(self, frame_id: str) -> str | None:
        pass

    @abstractmethod
    def close(self, id: str) -> None:
        pass


def get_frames_reference(feature):
    class FeatureReference(AbsFrames):
        @property
        def ids(self) -> list[str]:
            return feature.frame_ids

        @property
        def actives(self) -> list[str]:
            return feature.active_frame_ids

        def open(self, frame_id: str) -> str | None:
            return feature.open_frame(frame_id)

        def close(self, id: str):
            return feature.close_frame(id)

    return FeatureReference()
