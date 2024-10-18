from typing import Callable
from vx_logger import Logger
from vx_root.references.AbsFrames import AbsFrames
from vx_root.references.AbsParams import AbsParams
from vx_types import root_FeatureParams_dict
from .utils import FeatureUtils


class FeatureLifespan:
    def __init__(self):
        self.startup_callback: Callable[[], bool] | None = None
        self.shutdown_callback: Callable[[], bool] | None = None

    def startup_sequence(self) -> bool:
        if self.startup_callback:
            return self.startup_callback()
        return True

    def shutdown_sequence(self) -> bool:
        if self.shutdown_callback:
            return self.shutdown_callback()
        return True


class RootFeature:
    _instances = {}

    @classmethod
    def del_instance(cls, entry: str):
        feature_name = FeatureUtils.feature_name_from(entry)

        if feature_name in cls._instances:
            del cls._instances[feature_name]

    def __new__(cls, entry: str):
        feature_name = FeatureUtils.feature_name_from(entry)

        if feature_name not in cls._instances:
            cls._instances[feature_name] = super().__new__(cls)

        return cls._instances[feature_name]

    def __init__(self, entry: str) -> None:
        if not hasattr(self, "name"):
            self.name: str = FeatureUtils.feature_name_from(entry)
            self.root_params: root_FeatureParams_dict | None = None
            self.required_features: list[str] = []
            self.lifespan = FeatureLifespan()

            self.frames: AbsFrames = None
            self.params: AbsParams = None

    def init(self, value: root_FeatureParams_dict):
        self.root_params = value

    def set_required_features(self, value: list[str]):
        self.required_features = value

    def on_startup(self, callback: Callable[[], bool]):
        if self.lifespan.startup_callback:
            Logger.log(
                "Startup sequence already defined "
                f"in file: {self.lifespan.startup_callback.__code__.co_filename}, "
                f"at line: {self.lifespan.startup_callback.__code__.co_firstlineno}",
                "WARNING",
            )
        else:
            self.lifespan.startup_callback = callback

    def on_shutdown(self, callback: Callable[[], bool]):
        if self.lifespan.shutdown_callback:
            Logger.log(
                "Shutdown sequence already defined "
                f"in file: {self.lifespan.shutdown_callback.__code__.co_filename}, "
                f"at line: {self.lifespan.shutdown_callback.__code__.co_firstlineno}",
                "WARNING",
            )
        else:
            self.lifespan.shutdown_callback = callback
