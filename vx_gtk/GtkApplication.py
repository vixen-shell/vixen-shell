from .Gtk_imports import Gtk
from vx_logger import Logger


class GtkApplication(Gtk.Application):
    def __init__(self):
        super().__init__()

    def do_activate(self):
        self.hold()
        Logger.log("Gtk main loop is started")

    def quit(self):
        Logger.log("Gtk main loop is stopped")
        return super().quit()


GtkApp = GtkApplication()
