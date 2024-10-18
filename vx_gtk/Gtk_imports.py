import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.1")
gi.require_version("GtkLayerShell", "0.1")
gi.require_version("DbusmenuGtk3", "0.4")

from gi.repository import GLib, Gdk, Gtk, GtkLayerShell, WebKit2, DbusmenuGtk3

settings = Gtk.Settings.get_default()
settings.set_property("gtk-tooltip-timeout", 0)
