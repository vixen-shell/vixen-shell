import gi

gi.require_version("Gtk", "3.0")

from gi.repository import GLib, Gtk

from typing import Literal
from .AbstractLogger import AbstractLogger, get_logger_reference
from .AbstractFeature import AbstractFeature, get_feature_references
from .AbstractFeatures import AbstractFeatures, get_features_reference


class FeatureUtils:
    def init(self, logger, current_feature, features, show_dialog_box):
        self.Logger: AbstractLogger = get_logger_reference(logger)
        self.CurrentFeature: AbstractFeature = get_feature_references(current_feature)
        self.Features: AbstractFeatures = get_features_reference(features)
        self.show_dialog_box = show_dialog_box

    def show_dialog_box(
        self,
        message: str,
        level: Literal["INFO", "WARNING"] = "INFO",
        title: str = "Vixen Shell",
    ):
        pass
