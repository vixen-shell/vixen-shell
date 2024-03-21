import threading
from .Gtk_imports import Gtk
from ..log import Logger


class Gtk_main_loop:
    _thread = threading.Thread(target=Gtk.main)

    @staticmethod
    def run():
        Gtk_main_loop._thread.start()
        Logger.log("INFO", "Gtk main loop is started.")

    @staticmethod
    def quit():
        Gtk.main_quit()
        Gtk_main_loop._thread.join()
        Logger.log("INFO", "Gtk main loop is stopped.")
