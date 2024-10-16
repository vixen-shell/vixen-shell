import gi

gi.require_version("Gdk", "3.0")
from gi.repository import Gdk

from dasbus.connection import SessionMessageBus
from dasbus.specification import DBusSpecificationParser
from dasbus.client.observer import DBusObserver
from dasbus.client.proxy import disconnect_proxy
from dasbus.error import DBusError


def load_resource(resource_name):
    try:
        import importlib.resources as resources

        with resources.open_binary(__package__, resource_name) as resource_file:
            return resource_file.read()
    except:
        pass

    try:
        import importlib.util

        spec = importlib.util.find_spec(__package__)
        if (
            spec is not None
            and spec.loader is not None
            and hasattr(spec.loader, "get_data")
        ):
            return spec.loader.get_data(resource_name)
    except Exception:
        pass

    try:
        import pkgutil

        data = pkgutil.get_data(__package__, resource_name)
        if data is None:
            raise FileNotFoundError(
                f"Resource {resource_name} not found in package {__package__}."
            )
        return data
    except ImportError as e:
        raise ImportError(
            "Failed to load the resource using any available method."
        ) from e


PROPERTIES = [
    "Id",
    "Category",
    "Title",
    "Status",
    "WindowId",
    "IconName",
    "IconPixmap",
    "OverlayIconName",
    "OverlayIconPixmap",
    "AttentionIconName",
    "AttentionIconPixmap",
    "AttentionMovieName",
    "ToolTip",
    "IconThemePath",
    "ItemIsMenu",
    "Menu",
]


class StatusNotifierItem(object):
    def __init__(self, service_name, object_path):
        self.service_name = service_name
        self.object_path = object_path
        self.on_loaded_callback = None
        self.on_updated_callback = None
        self.session_bus = SessionMessageBus()
        self.properties = {"ItemIsMenu": True}
        self.item_proxy = None

        self.item_observer = DBusObserver(
            message_bus=self.session_bus, service_name=self.service_name
        )
        self.item_observer.service_available.connect(self.item_available_handler)
        self.item_observer.service_unavailable.connect(self.item_unavailable_handler)
        self.item_observer.connect_once_available()

    def __del__(self):
        if self.item_proxy is not None:
            disconnect_proxy(self.item_proxy)
        self.item_observer.disconnect()
        self.session_bus.disconnect()

    def item_available_handler(self, _observer):
        self.item_proxy = self.session_bus.get_proxy(
            self.service_name, self.object_path
        )
        try:
            spec = self.item_proxy._handler.specification
            if spec is not None:
                if not any(
                    "StatusNotifierItem" in ifname for ifname in spec.interfaces
                ):
                    DBusSpecificationParser._parse_xml(
                        spec,
                        load_resource("org.kde.StatusNotifierItem.xml"),
                    )
        except:
            pass
        if hasattr(self.item_proxy, "PropertiesChanged"):
            self.item_proxy.PropertiesChanged.connect(
                lambda _if, changed, invalid: self.change_handler(
                    list(changed), invalid
                )
            )
        if hasattr(self.item_proxy, "NewTitle"):
            self.item_proxy.NewTitle.connect(lambda: self.change_handler(["Title"]))
        if hasattr(self.item_proxy, "NewIcon"):
            self.item_proxy.NewIcon.connect(lambda: self.change_handler(["IconName"]))
        if hasattr(self.item_proxy, "NewAttentionIcon"):
            self.item_proxy.NewAttentionIcon.connect(
                lambda: self.change_handler(["AttentionIconName"])
            )
        if hasattr(self.item_proxy, "NewIconThemePath"):
            self.item_proxy.NewIconThemePath.connect(
                lambda _icon_theme_path: self.change_handler(["IconThemePath"])
            )
        if hasattr(self.item_proxy, "NewStatus"):
            self.item_proxy.NewStatus.connect(
                lambda _status: self.change_handler(["Status"])
            )
        for name in PROPERTIES:
            try:
                self.properties[name] = getattr(self.item_proxy, name)
            except (AttributeError, DBusError):
                # remote StatusNotifierItem object does not support all SNI properties
                pass
        if self.on_loaded_callback is not None:
            self.on_loaded_callback(self)

    def item_unavailable_handler(self, _observer):
        disconnect_proxy(self.item_proxy)
        self.item_proxy = None

    def change_handler(
        self, changed_properties: list[str], invalid_properties: list[str] = None
    ):
        if invalid_properties is None:
            invalid_properties = []
        actual_changed_properties = []
        if len(changed_properties) > 0:
            for name in changed_properties:
                try:
                    self.properties[name] = getattr(self.item_proxy, name)
                    actual_changed_properties.append(name)
                except (AttributeError, DBusError):
                    pass
        if len(invalid_properties) > 0:
            for name in invalid_properties:
                if name in self.properties:
                    self.properties.pop(name)
        if len(actual_changed_properties) > 0:
            if self.on_updated_callback is not None:
                self.on_updated_callback(self, actual_changed_properties)

    def set_on_loaded_callback(self, callback):
        self.on_loaded_callback = callback

    def set_on_updated_callback(self, callback):
        self.on_updated_callback = callback

    @property
    def item_is_menu(self):
        if "ItemIsMenu" in self.properties:
            return self.properties["ItemIsMenu"]
        else:
            return False

    def context_menu(self, event: Gdk.EventButton):
        self.item_proxy.ContextMenu(event.x, event.y)

    def activate(self, event: Gdk.EventButton):
        self.item_proxy.Activate(event.x, event.y)

    def secondary_action(self, event: Gdk.EventButton):
        self.item_proxy.SecondaryAction(event.x, event.y)

    def scroll(self, distance, direction):
        self.item_proxy.Scroll(distance, direction)
