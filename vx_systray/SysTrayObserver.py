import gi, socket, json, threading, os, time, asyncio

gi.require_version("DbusmenuGtk3", "0.4")
from gi.repository import GLib, DbusmenuGtk3
from fastapi import WebSocket
from vx_shell.logger import Logger
from .socket_worker import start_worker


class SysTrayState:
    state = []
    menus = {}
    websockets: list[WebSocket] = []

    @staticmethod
    def check_available_menu(data: dict):
        service_name = data["service_name"]
        menu_info = data.get("menu")

        if not menu_info:

            def process():
                if service_name in SysTrayState.menus:
                    SysTrayState.menus.pop(service_name)

            GLib.idle_add(process)

        else:

            def process():
                if not service_name in SysTrayState.menus:
                    SysTrayState.menus[service_name] = DbusmenuGtk3.Menu().new(
                        dbus_name=menu_info["dbus_name"],
                        dbus_object=menu_info["dbus_object"],
                    )

            GLib.idle_add(process)

    @staticmethod
    def handle_event(event: dict):
        event_id = event["id"]
        data = event["data"]

        if event_id == "ADD_ITEM":
            SysTrayState.state.append(data)

        if event_id == "UPDATE_ITEM":
            SysTrayState.state = [
                data if item.get("service_name") == data["service_name"] else item
                for item in SysTrayState.state
            ]

        if event_id == "REMOVE_ITEM":
            SysTrayState.state = list(
                filter(
                    lambda item: item.get("service_name") != data["service_name"],
                    SysTrayState.state,
                )
            )

        SysTrayState.check_available_menu(data)

        for websocket in SysTrayState.websockets:
            asyncio.run(
                websocket.send_json(
                    {"id": "UPDATE", "data": {"systray": SysTrayState.state}}
                )
            )


class SysTrayObserver:
    _thread: threading.Thread = None
    _writer = None
    _stop_event = threading.Event()

    _socket_path = "/tmp/vx_systray_socket"
    _worker_process = None
    _worker_path = None

    @staticmethod
    def listener_thread():
        socket_path_found = False

        while not socket_path_found:
            if os.path.exists(SysTrayObserver._socket_path):
                socket_path_found = True

            time.sleep(0.25)

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect(SysTrayObserver._socket_path)
            SysTrayObserver._writer = sock

            Logger.log("[Systray]: Start listening")
            while not SysTrayObserver._stop_event.is_set():
                try:
                    data = sock.recv(1024)
                    if not data:
                        break

                    SysTrayState.handle_event(json.loads(data.decode()))

                except Exception as e:
                    Logger.log(f"[Systray]: Error in listener thread: {e}")
                    break

    @staticmethod
    def start() -> bool:
        if not SysTrayObserver._thread:
            if os.path.exists(SysTrayObserver._socket_path):
                os.remove(SysTrayObserver._socket_path)

            Logger.log("[Systray]: Start worker")
            SysTrayObserver._worker_path, SysTrayObserver._worker_process = (
                start_worker()
            )

            SysTrayObserver._stop_event.clear()
            SysTrayObserver._thread = threading.Thread(
                target=SysTrayObserver.listener_thread
            )
            SysTrayObserver._thread.start()

            return True

    @staticmethod
    def stop():
        if SysTrayObserver._thread:
            Logger.log("[Systray]: Stop event listener")
            SysTrayObserver._stop_event.set()
            SysTrayObserver._thread.join()
            SysTrayObserver._thread = None

            Logger.log("[Systray]: Stop worker")
            SysTrayObserver._worker_process.kill()
            os.remove(SysTrayObserver._worker_path)
