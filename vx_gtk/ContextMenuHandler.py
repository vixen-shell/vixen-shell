from .Gtk_imports import GLib, Gtk
from typing import Callable, TypedDict, Literal, Dict, Union

type MenuSeparator = Literal["separator"]

type ContextMenu = Dict[str, Union[MenuItem, MenuSeparator]]


class MenuItem(TypedDict):
    icon: str
    entry: Callable[[], None] | ContextMenu


test: ContextMenu = {"Open": {"entry": lambda: print("Open")}}


def get_item_with_icon(label: str, icon_name: str):
    item = Gtk.MenuItem()
    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    image = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
    label_widget = Gtk.Label(label)
    box.pack_start(image, False, False, 0)
    box.pack_start(label_widget, False, False, 0)
    item.add(box)

    return item


def new_menu_item(label: str, callback: Callable[[], None], icon_name: str = None):
    def item_callback(widget):
        callback()

    item = (
        Gtk.MenuItem(label=label)
        if not icon_name
        else get_item_with_icon(label, icon_name)
    )
    item.connect("activate", item_callback)
    item.show_all()

    return item


def new_submenu_item(label: str, submenu: Gtk.Menu, icon_name: str = None):
    item = (
        Gtk.MenuItem(label=label)
        if not icon_name
        else get_item_with_icon(label, icon_name)
    )
    item.set_submenu(submenu)
    item.show_all()

    return item


def new_separator_menu_item():
    separator = Gtk.SeparatorMenuItem()
    separator.show()

    return separator


def get_gtk_menu(object: ContextMenu):
    menu = Gtk.Menu()

    for key, value in object.items():
        if value == "separator":
            menu.append(new_separator_menu_item())
        else:
            label = key
            icon_name = value.get("icon")
            entry = value.get("entry")

            if callable(entry):
                menu.append(new_menu_item(label, entry, icon_name))

            if isinstance(entry, dict):
                menu.append(new_submenu_item(label, get_gtk_menu(entry), icon_name))

    return menu


class ContextMenuHandler:
    def __init__(self, context_menu_object: ContextMenu):
        self.menu = get_gtk_menu(context_menu_object)
        self.menu.show()
