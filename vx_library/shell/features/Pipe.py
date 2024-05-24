from fastapi import WebSocket


class WebSocketClientHandler:
    def __init__(self) -> None:
        self.clients: list[WebSocket] = []

    def add_client(self, websocket: WebSocket):
        self.clients.append(websocket)

    def remove_client(self, websocket: WebSocket):
        self.clients.remove(websocket)
