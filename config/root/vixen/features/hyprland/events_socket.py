from fastapi import WebSocket
from . import content
from .hypr_events import HyprEventsListener


@content.add("socket")
async def events(websocket: WebSocket):
    try:
        HyprEventsListener.attach_websocket(websocket)

        while True:
            text = await websocket.receive_text()
            if text == "close":
                HyprEventsListener.detach_websocket(websocket)
                await websocket.close()
                break
    except:
        HyprEventsListener.detach_websocket(websocket)
