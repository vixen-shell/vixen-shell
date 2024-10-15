import socket, json, threading, os, time, asyncio
from typing import List
from fastapi import WebSocket
from vx_shell.logger import Logger
from .socket_worker import start_worker


class SysTrayObserver:
    _thread: threading.Thread = None
    _websockets: List[WebSocket] = []
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

                    json_data: dict = json.loads(data.decode())
                    print(json_data)

                    for websocket in SysTrayObserver._websockets:
                        asyncio.create_task(websocket.send_json(json_data))
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

    @staticmethod
    def attach_websocket(websocket: WebSocket):
        SysTrayObserver._websockets.append(websocket)

    @staticmethod
    def detach_websocket(websocket: WebSocket):
        SysTrayObserver._websockets.remove(websocket)
