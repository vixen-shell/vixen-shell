import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from vx_root import root_content


@root_content().dispatch("file")
def icon(icon_name: str):
    icon_theme = Gtk.IconTheme.get_default()

    icon_info = (
        icon_theme.lookup_icon(icon_name, Gtk.IconSize.DIALOG, 0)
        or icon_theme.lookup_icon("image-missing-symbolic", Gtk.IconSize.DIALOG, 0)
        or icon_theme.lookup_icon("image-missing", Gtk.IconSize.DIALOG, 0)
    )

    icon_filepath = icon_info.get_filename()
    return icon_filepath
