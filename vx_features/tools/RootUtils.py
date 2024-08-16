from typing import Literal
from .AbstractLogger import AbstractLogger, get_logger_reference
from .AbstractFeatures import AbstractFeatures, get_features_reference
from .AbstractParams import AbstractParams, get_params_references
from ..utils import feature_name_from


class RootUtils:
    _instances = {}

    @classmethod
    def del_instance(cls, entry: str):
        feature_name = feature_name_from(entry)

        if feature_name in cls._instances:
            del cls._instances[feature_name]

    def __new__(cls, entry: str):
        feature_name = feature_name_from(entry)

        if feature_name not in cls._instances:
            cls._instances[feature_name] = super().__new__(cls)

        return cls._instances[feature_name]

    def __init__(self, entry: str) -> None:
        if not hasattr(self, "_RootUtils__feature_name"):
            self.__feature_name: str = feature_name_from(entry)

    def init(self, logger, features, show_dialog_box):
        self.Logger: AbstractLogger = get_logger_reference(logger)
        self.Params: AbstractParams = get_params_references(self.__feature_name)
        self.Features: AbstractFeatures = get_features_reference(features)
        self.show_dialog_box = show_dialog_box

    def show_dialog_box(
        self,
        message: str,
        level: Literal["INFO", "WARNING"] = "INFO",
        title: str = "Vixen Shell",
    ):
        pass
