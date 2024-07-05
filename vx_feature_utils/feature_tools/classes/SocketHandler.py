from fastapi import WebSocket


class SocketHandler:
    async def on_opening(self, websocket: WebSocket):
        pass

    async def on_loop_iteration(self, websocket: WebSocket):
        await websocket.receive_text()

    async def on_closing(self, websocket: WebSocket):
        pass
