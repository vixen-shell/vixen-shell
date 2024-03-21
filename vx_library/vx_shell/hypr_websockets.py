from fastapi import WebSocket
from .api import api
from .hypr_events import HYPR_SOCKET_PATH, HyprSocketDataHandler, UnixSocket


@api.websocket("/hypr/events")
async def websocket_hypr_events(websocket: WebSocket):
    hypr_socket = UnixSocket(HYPR_SOCKET_PATH)
    await websocket.accept()

    try:
        if await hypr_socket.open_connection():
            while True:
                data = HyprSocketDataHandler(await hypr_socket.reader.readline())
                await websocket.send_json(data.to_json)

    except:
        await hypr_socket.close_connection()
