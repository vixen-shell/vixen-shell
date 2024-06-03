from typing import Literal
from .Gtk_imports import Gtk, GLib


def show_dialog_box(message: str, level: Literal["INFO", "WARNING"] = "INFO"):
    message_type = {"INFO": 0, "WARNING": 1}.get(level)

    def process():
        dialog = Gtk.MessageDialog(
            transient_for=None,
            flags=0,
            message_type=message_type,
            buttons=Gtk.ButtonsType.OK,
            text="Vixen Shell",
        )
        dialog.format_secondary_text(message)

        def on_dialog_response(dialog, response_id):
            dialog.destroy()

        dialog.connect("response", on_dialog_response)
        dialog.show()

    GLib.idle_add(process)
