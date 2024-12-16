import subprocess, os, json, locale, asyncio

from typing import Callable, TypedDict, Any, Literal, Optional
from fastapi import WebSocket
from vx_path import VxPath


class OutputEvent(TypedDict):
    id: str
    data: Optional[dict]


class StateItem(TypedDict):
    key: str
    value: Any


class VxConfig:
    websockets: list[WebSocket] = []
    listeners: list[Callable[[StateItem], None]] = []

    API_PORT: int = 6481
    FRONT_PORT: int = 6492
    FRONT_DEV_PORT: int = 5173
    ALLOWED_DOMAINS: list[str] = [
        "about:blank",
        f"localhost:{FRONT_PORT}",
        f"localhost:{FRONT_DEV_PORT}",
        "vixen-shell.github.io",
    ]

    STATE: dict = {
        "vx_ui_scale": 1.0,
        "vx_ui_color_scheme": None,
        "vx_ui_color": "teal",
        "vx_ui_icons": "regular",
        "vx_ui_font_family": None,
        "vx_ui_font_family_monospace": None,
    }

    @staticmethod
    def dispatch_websocket_event(event: OutputEvent):
        for websocket in VxConfig.websockets:
            asyncio.create_task(websocket.send_json(event))

    @staticmethod
    def gtk_fonts():
        def get_gtk_font_name(monospace: bool = False):
            return (
                subprocess.run(
                    [
                        "gsettings",
                        "get",
                        "org.gnome.desktop.interface",
                        f"{'monospace-' if monospace else ''}font-name",
                    ],
                    stdout=subprocess.PIPE,
                    text=True,
                )
                .stdout.strip()
                .strip("'")
                .rsplit(" ", 1)[0]
            )

        font_family = get_gtk_font_name()
        font_family_monospace = get_gtk_font_name(True)

        return {
            "font_family": font_family,
            "font_family_monospace": font_family_monospace,
        }

    @staticmethod
    def locale():
        return locale.getlocale()[0] or "en_US"

    @staticmethod
    def load():
        file_path = VxPath.VX_CONFIG_FILE

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                vx_config: dict = json.load(file)

                VxConfig.API_PORT = vx_config.get("api_port")
                VxConfig.FRONT_PORT = vx_config.get("front_port")
                VxConfig.FRONT_DEV_PORT = vx_config.get("front_dev_port")
                VxConfig.STATE = vx_config.get("state")
        else:
            VxConfig.save()

    @staticmethod
    def save():
        file_path = VxPath.VX_CONFIG_FILE

        data = {
            "api_port": VxConfig.API_PORT,
            "front_port": VxConfig.FRONT_PORT,
            "front_dev_port": VxConfig.FRONT_DEV_PORT,
            "state": VxConfig.STATE,
        }

        if os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        else:
            with open(file_path, "x", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

    @staticmethod
    def save_state():
        file_path = VxPath.VX_CONFIG_FILE

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Unable to found '{file_path}' file")

        with open(file_path, "r", encoding="utf-8") as file:
            vx_config: dict = json.load(file)
            vx_config["state"] = VxConfig.STATE

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(vx_config, file, indent=4, ensure_ascii=False)

        VxConfig.dispatch_websocket_event(OutputEvent(id="SAVE", data=VxConfig.STATE))

    @staticmethod
    def save_state_items(
        keys: list[str], option: Literal["update", "add", "remove"] = "update"
    ):
        file_path = VxPath.VX_CONFIG_FILE

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Unable to found '{file_path}' file")

        with open(file_path, "r", encoding="utf-8") as file:
            vx_config: dict = json.load(file)

            for key in keys:
                if option == "update" or option == "add":
                    if not key in vx_config["state"] and option == "update":
                        raise KeyError(f"'{key}' state key not found")

                    vx_config["state"][key] = VxConfig.STATE[key]

                elif option == "remove":
                    del vx_config["state"][key]

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(vx_config, file, indent=4, ensure_ascii=False)

        if option == "update":
            VxConfig.dispatch_websocket_event(
                OutputEvent(id="SAVE_ITEMS", data={"keys": keys})
            )

    @staticmethod
    def add_state_listener(listener: Callable[[StateItem], None]):
        if not listener in VxConfig.listeners:
            VxConfig.listeners.append(listener)

    @staticmethod
    def remove_state_listener(listener: Callable[[StateItem], None]):
        if listener in VxConfig.listeners:
            VxConfig.listeners.remove(listener)

    @staticmethod
    def update_state(
        feature_state: dict, option: Literal["add", "remove"] = "add", save: bool = True
    ):
        keys_processed: list[str] = []

        if option == "add":
            for key, value in feature_state.items():
                if key in VxConfig.STATE:
                    raise KeyError(f"'{key}' state key already exists")

                VxConfig.STATE[key] = value
                keys_processed.append(key)

        if option == "remove":
            for key in feature_state.keys():
                if not key in VxConfig.STATE:
                    raise KeyError(f"'{key}' state key not found")

                VxConfig.STATE.pop(key, None)
                keys_processed.append(key)

        if save:
            VxConfig.save_state_items(keys_processed, option)

    @staticmethod
    def get_state(key: str):
        if not key in VxConfig.STATE:
            raise KeyError(f"'{key}' state key not found")

        return VxConfig.STATE[key]

    @staticmethod
    def set_state(key: str, value: Any):
        if not key in VxConfig.STATE:
            raise KeyError(f"'{key}' state key not found")

        VxConfig.STATE[key] = value

        VxConfig.dispatch_websocket_event(
            OutputEvent(
                id="UPDATE",
                data={"key": key, "value": value},
            )
        )

        for listener in VxConfig.listeners:
            listener(StateItem(key=key, value=value))
