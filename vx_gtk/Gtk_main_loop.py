import threading
from vx_logger import Logger
from .Gtk_imports import Gtk


class GtkMainLoop:
    _thread = threading.Thread(target=Gtk.main)

    @staticmethod
    def run():
        GtkMainLoop._thread.start()
        Logger.log("Gtk main loop is started")

    @staticmethod
    def quit():
        Gtk.main_quit()
        GtkMainLoop._thread.join()
        Logger.log("Gtk main loop is stopped")
