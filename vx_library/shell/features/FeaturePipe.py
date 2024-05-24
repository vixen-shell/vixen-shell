from fastapi import WebSocket
from websockets import ConnectionClosedError
from typing import Dict
from .pipe_events import OutputEvent
from ..logger import Logger


class FeaturePipe:
    def __init__(self):
        self.pipe_is_opened = False
        self.client_websockets: Dict[str, WebSocket] = {}

    def open_pipe(self):
        if not self.pipe_is_opened:
            self.pipe_is_opened = True

    async def close_pipe(self):
        if self.pipe_is_opened:
            # await self.disconnect_client("Pipe closed")
            self.pipe_is_opened = False

    async def connect_client(self, client_id: str, websocket: WebSocket):
        if not self.pipe_is_opened:
            raise Exception("Pipe is closed")

        if client_id in self.client_websockets:
            raise Exception(f"Client '{client_id}' already connected")

        self.client_websockets[client_id] = websocket

    def remove_client(self, client_id: str):
        if client_id in self.client_websockets:
            del self.client_websockets[client_id]

    # async def disconnect_client(self, reason: str, client_id: str | None = None):
    #     async def disconnect(id: str):
    #         if id in self.client_websockets:
    #             await self.client_websockets[id].close(reason=reason)
    #             self.remove_client(id)

    #     if not client_id:
    #         ids = list(self.client_websockets.keys())
    #         for id in ids:
    #             await disconnect(id)
    #     else:
    #         await disconnect(client_id)

    async def dispatch_event(self, event: OutputEvent, client_id: str | None = None):
        ids = list(self.client_websockets.keys())

        for id in ids:
            if client_id and id == client_id:
                continue
            try:
                await self.client_websockets[id].send_json(event)
            except ConnectionClosedError:
                Logger.log(
                    f"Aborting sending '{event['id']}' event: WebSocket client '{id}' closed.",
                    "WARNING",
                )
            except Exception as exception:
                Logger.log(exception, "ERROR")
