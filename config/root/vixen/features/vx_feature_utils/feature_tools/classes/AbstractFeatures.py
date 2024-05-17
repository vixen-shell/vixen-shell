from abc import ABC, abstractmethod
from .AbstractFeature import AbstractFeature, get_feature_references


class AbstractFeatures:
    @abstractmethod
    def names(self) -> list[str]:
        pass

    @abstractmethod
    def exists(self, name: str) -> bool:
        pass

    @abstractmethod
    def get(self, name: str) -> AbstractFeature | None:
        pass


def get_features_reference(features):
    class FeaturesReferences(AbstractFeatures):
        def names(self) -> list[str]:
            return features.names()

        def exists(self, name: str) -> bool:
            return features.exists(name)

        def get(self, name: str) -> AbstractFeature | None:
            feature = features.get(name)
            return get_feature_references(feature) if feature else None

    return FeaturesReferences()
