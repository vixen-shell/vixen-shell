from typing import Literal, Callable
from .Gtk_imports import Gtk, GLib


def show_message_dialog(
    text: str,
    title: str = None,
    details: str = None,
    level: Literal["INFO", "WARNING"] = "INFO",
):
    message_type = {"INFO": 0, "WARNING": 1}.get(level)

    def process():
        dialog = Gtk.MessageDialog(
            transient_for=None,
            flags=0,
            message_type=message_type,
            buttons=Gtk.ButtonsType.OK,
            text=text,
            title=title,
        )

        if not title:
            dialog.set_decorated(False)

        if details:
            dialog.format_secondary_text(details)

        def on_dialog_response(dialog, response_id):
            dialog.destroy()

        dialog.connect("response", on_dialog_response)
        dialog.show()

    GLib.idle_add(process)


def show_confirm_dialog(
    text: str,
    ok_callback: Callable[[], None],
    cancel_callback: Callable[[], None] = None,
    title: str = None,
    details: str = None,
):
    def process():
        dialog = Gtk.MessageDialog(
            transient_for=None,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=text,
            title=title,
        )

        if not title:
            dialog.set_decorated(False)

        if details:
            dialog.format_secondary_text(details)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            ok_callback()
        elif response == Gtk.ResponseType.CANCEL:
            if cancel_callback:
                cancel_callback()

        dialog.destroy()

    GLib.idle_add(process)
