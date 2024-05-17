from vx_feature_utils import Utils
from fastapi import WebSocket

utils = Utils.define_feature_utils()
content = Utils.define_feature_content({"autostart": True})

from .hypr_events import HyprEventsListener


@content.on_startup
def on_startup():
    HyprEventsListener.start()


@content.on_shutdown
def on_shutdown():
    HyprEventsListener.stop()


@content.add("websocket")
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
