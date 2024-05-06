from fastapi import WebSocket
from ..api import api
from ...hypr_events import HyprEventsListener

# ---------------------------------------------- - - -
# HYPR EVENTS (SOCKET2)
#


@api.websocket("/hypr/events")
async def websocket_hypr_events(websocket: WebSocket):
    await websocket.accept()

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
