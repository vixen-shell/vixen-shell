import gi

gi.require_version("Gtk", "3.0")

from gi.repository import GLib, Gtk

from typing import Literal
from .AbstractLogger import AbstractLogger, get_logger_reference
from .AbstractFeature import AbstractFeature, get_feature_references
from .AbstractFeatures import AbstractFeatures, get_features_reference


class FeatureUtils:
    def init(self, logger, current_feature, features):
        self.Logger: AbstractLogger = get_logger_reference(logger)
        self.CurrentFeature: AbstractFeature = get_feature_references(current_feature)
        self.Features: AbstractFeatures = get_features_reference(features)

    def show_dialog_box(
        message: str,
        level: Literal["INFO", "WARNING"] = "INFO",
        title: str = "Vixen Shell",
    ):
        message_type = {"INFO": 0, "WARNING": 1}.get(level)

        def process():
            dialog = Gtk.MessageDialog(
                transient_for=None,
                flags=0,
                message_type=message_type,
                buttons=Gtk.ButtonsType.OK,
                text=title,
            )
            dialog.format_secondary_text(message)

            def on_dialog_response(dialog, response_id):
                dialog.destroy()

            dialog.connect("response", on_dialog_response)
            dialog.show()

        GLib.idle_add(process)
