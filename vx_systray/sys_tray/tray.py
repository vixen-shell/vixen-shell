import typing, json
from socket import socket
from .item import StatusNotifierItem
from .menu import MenuObserver


def update_tooltip(item):
    icon_name, icon_data, title, description = (
        item.properties["ToolTip"]
        if "ToolTip" in item.properties
        else item.properties["Tooltip"]
    )

    tooltip = title

    if description:
        tooltip = "<b>{}</b>\n{}".format(title, description)

    return tooltip


class Tray:
    def __init__(self, socket: socket):
        self.items = {}
        self.socket = socket

    def print_event(
        self,
        event_id: typing.Literal["ADD_ITEM", "UPDATE_ITEM", "REMOVE_ITEM"],
        item: dict | None = None,
    ):
        self.socket.sendall(
            json.dumps(
                {
                    "id": event_id,
                    "data": item,
                }
            ).encode()
        )

    def add_item(self, item: StatusNotifierItem):
        full_service_name = "{}{}".format(item.service_name, item.object_path)

        icon_name = None
        tooltip = None
        status = None
        menu = None

        if full_service_name not in self.items:
            if "IconName" in item.properties and len(item.properties["IconName"]) > 0:
                icon_name = item.properties["IconName"]

            if "Tooltip" in item.properties or "ToolTip" in item.properties:
                tooltip = update_tooltip(item)
            elif "Title" in item.properties:
                tooltip = item.properties["Title"]

            if "Status" in item.properties:
                status = item.properties["Status"].lower()

            self.items[full_service_name] = {
                "service_name": full_service_name,
                "icon_name": icon_name,
                "tooltip": tooltip,
                "status": status,
                "menu": menu,
            }

            if "Menu" in item.properties:
                MenuObserver(item, self)

            self.print_event("ADD_ITEM", self.items[full_service_name])

    def update_item(self, item: StatusNotifierItem, changed_properties: list[str]):
        full_service_name = "{}{}".format(item.service_name, item.object_path)

        icon_name = self.items[full_service_name].get("icon_name")
        tooltip = self.items[full_service_name].get("tooltip")
        status = self.items[full_service_name].get("status")

        if "IconName" in changed_properties and len(item.properties["IconName"]) > 0:
            icon_name = item.properties["IconName"]

        if "Tooltip" in changed_properties or "ToolTip" in changed_properties:
            tooltip = update_tooltip(item)
        elif "Title" in changed_properties:
            tooltip = item.properties["Title"]

        if "Status" in item.properties:
            status = item.properties["Status"].lower()

        self.items[full_service_name]["icon_name"] = icon_name
        self.items[full_service_name]["tooltip"] = tooltip
        self.items[full_service_name]["status"] = status

        self.print_event("UPDATE_ITEM", self.items[full_service_name])

    def remove_item(self, item: StatusNotifierItem):
        full_service_name = "{}{}".format(item.service_name, item.object_path)
        self.print_event("REMOVE_ITEM", {"service_name": full_service_name})
        self.items.pop(full_service_name)
