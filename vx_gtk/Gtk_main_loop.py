import threading
from vx_logger import Logger
from .Gtk_imports import Gtk, GLib


class GtkMainLoop:
    _thread = threading.Thread(target=Gtk.main)

    @staticmethod
    def run():
        GtkMainLoop._thread.start()
        Logger.log("Gtk main loop is started")

    @staticmethod
    def quit():
        def process():
            Gtk.main_quit()

        GLib.idle_add(process)
        GtkMainLoop._thread.join()
        Logger.log("Gtk main loop is stopped")
