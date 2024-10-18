from vx_gtk import Gtk
from typing import Callable, TypedDict, Literal, Dict, Union

type Separator = Literal["separator"]

type Menu = Dict[str, Union[MenuItem, Separator]]


class MenuItem(TypedDict):
    icon: str
    entry: Callable[[], None] | Menu


test: Menu = {"Open": {"entry": lambda: print("Open")}}


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


class ContextMenu:
    def __init__(self):
        self.menu = Gtk.Menu()
        self.menu.show()

    def add_item(
        self,
        label: str,
        icon_name: str = None,
        end_separator: bool = False,
    ):
        def decorator(callback: Callable[[], None]):
            self.menu.append(new_menu_item(label, callback, icon_name))

            if end_separator:
                self.menu.append(new_separator_menu_item())

            return callback

        return decorator

    def add_submenu(
        self,
        label: str,
        icon_name: str = None,
        end_separator: bool = False,
    ):
        def decorator(callback: Callable[[], ContextMenu]):
            submenu = callback().menu

            self.menu.append(new_submenu_item(label, submenu, icon_name))

            if end_separator:
                self.menu.append(new_separator_menu_item())

            return callback

        return decorator
