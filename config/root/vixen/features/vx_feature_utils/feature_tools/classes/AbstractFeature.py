import asyncio
from abc import ABC, abstractmethod
from typing import Any
from .FeatureContent import ContentType


class AbstractFeature(ABC):
    @property
    @abstractmethod
    def frame_ids(self) -> list[str]:
        pass

    @property
    @abstractmethod
    def active_frame_ids(self) -> list[str]:
        pass

    @abstractmethod
    def get_content(self, content_type: ContentType, name: str) -> Any:
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def open_frame(self, frame_id: str) -> str | None:
        pass

    @abstractmethod
    def close_frame(self, id: str):
        pass


def get_feature_references(feature):
    class FeatureReference(AbstractFeature):
        @property
        def frame_ids(self) -> list[str]:
            return feature.frame_ids

        @property
        def active_frame_ids(self) -> list[str]:
            return feature.active_frame_ids

        def get_content(self, content_type: ContentType, name: str) -> Any:
            return feature.content.get(content_type, name)

        def start(self):
            feature.start()

        def stop(self):
            asyncio.create_task(feature.stop())

        def open_frame(self, frame_id: str) -> str | None:
            return feature.open_frame(frame_id)

        def close_frame(self, id: str):
            feature.close_frame(id)

    return FeatureReference()
