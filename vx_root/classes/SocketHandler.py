from fastapi import WebSocket
from typing import TypedDict, Union, Dict, Any, Coroutine


class SocketEvent(TypedDict):
    id: str
    data: Union[Dict[str, Any] | None]


class SocketHandler:
    def __init__(self, websocket: WebSocket) -> None:
        self.websocket: WebSocket = websocket

    async def on_opening(self):
        pass

    async def on_loop_iteration(self):
        await self.websocket.receive_text()

    async def on_closing(self) -> Coroutine:
        pass
