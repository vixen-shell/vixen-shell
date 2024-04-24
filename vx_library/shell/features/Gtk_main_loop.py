import threading
from .Gtk_imports import Gdk, Gtk
from ..logger import Logger


def init_style_context():
    stylesheet = b"""
    #layer_frame {
        background-color: transparent;
    }
    #window_frame {
        background-color: #242424;
    }
    """
    style_provider = Gtk.CssProvider()
    style_provider.load_from_data(stylesheet)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        style_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )


class Gtk_main_loop:
    _thread = threading.Thread(target=Gtk.main)

    @staticmethod
    def run():
        Gtk_main_loop._thread.start()
        init_style_context()
        Logger.log("Gtk main loop is started")

    @staticmethod
    def quit():
        Gtk.main_quit()
        Gtk_main_loop._thread.join()
        Logger.log("Gtk main loop is stopped")
