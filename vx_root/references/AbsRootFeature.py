from inspect import stack, getmodule
from abc import ABC, abstractmethod
from typing import Callable
from vx_types import root_FeatureParams_dict
from .AbsFrames import AbsFrames
from .AbsParams import AbsParams


class AbsRootFeature(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def frames(self) -> AbsFrames:
        pass

    @property
    @abstractmethod
    def params(self) -> AbsParams:
        pass

    @abstractmethod
    def init(self, value: root_FeatureParams_dict) -> None:
        pass

    @abstractmethod
    def set_required_features(self, value: list[str]) -> None:
        pass

    @abstractmethod
    def on_startup(self, callback: Callable[[], bool]) -> None:
        pass

    @abstractmethod
    def on_shutdown(self, callback: Callable[[], bool]) -> None:
        pass


def get_root_feature_reference(root_feature):
    def restricted(feature_name: str = None):
        def decorator(attribute):
            def wrapper(*args, **kwargs):
                package_name = getmodule(stack()[1].frame).__package__

                if not package_name:
                    raise PermissionError(
                        f"The usage of the '{attribute.__name__}' attribute only "
                        "applies in the context of a feature package"
                    )

                if feature_name:
                    if not package_name.split(".")[0] == feature_name:
                        raise PermissionError(
                            f"The usage of the '{attribute.__name__}' attribute is only "
                            "applicable in the context of the original feature package"
                        )

                return attribute(*args, **kwargs)

            return wrapper

        return decorator

    class RootFeatureReference(AbsRootFeature):
        @property
        @restricted()
        def name(self) -> str:
            return root_feature.name

        @property
        @restricted()
        def frames(self) -> AbsFrames:
            return root_feature.frames

        @property
        @restricted()
        def params(self) -> AbsParams:
            return root_feature.params

        @restricted(root_feature.name)
        def init(self, value: root_FeatureParams_dict) -> None:
            return root_feature.init(value)

        @restricted(root_feature.name)
        def set_required_features(self, value: list[str]) -> None:
            return root_feature.set_required_features(value)

        @restricted(root_feature.name)
        def on_startup(self, callback: Callable[[], bool]) -> None:
            return root_feature.on_startup(callback)

        @restricted(root_feature.name)
        def on_shutdown(self, callback: Callable[[], bool]) -> None:
            return root_feature.on_shutdown(callback)

    return RootFeatureReference()
