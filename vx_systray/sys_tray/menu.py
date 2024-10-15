from dasbus.connection import SessionMessageBus
from dasbus.client.observer import DBusObserver


class MenuObserver(object):
    def __init__(self, item, tray):
        self.item = item
        self.tray = tray

        self.service_name = self.item.service_name
        self.object_path = self.item.properties["Menu"]

        self.session_bus = SessionMessageBus()

        self.menu_observer = DBusObserver(
            message_bus=self.session_bus, service_name=self.service_name
        )
        self.menu_observer.service_available.connect(self.menu_available_handler)
        self.menu_observer.service_unavailable.connect(self.menu_unavailable_handler)
        self.menu_observer.connect_once_available()

    def __del__(self):
        self.menu_observer.disconnect()
        self.session_bus.disconnect()

    def menu_available_handler(self, _observer):
        full_service_name = "{}{}".format(self.item.service_name, self.item.object_path)

        available_menu_info = {
            "service_name": self.service_name,
            "object_path": self.object_path,
        }

        if self.tray.items[full_service_name].get("menu") != available_menu_info:
            self.tray.items[full_service_name]["menu"] = available_menu_info
            self.tray.update_item(self.item, ["menu"])

    def menu_unavailable_handler(self, _observer):
        full_service_name = "{}{}".format(self.item.service_name, self.item.object_path)

        if self.tray.items[full_service_name].get("menu") is not None:
            self.tray.items[full_service_name]["menu"] = None
            self.tray.update_item(self.item, ["menu"])
