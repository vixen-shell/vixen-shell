from vx_feature_utils import define_feature
from fastapi import WebSocket

feature = define_feature({"autostart": True})

from .hypr_events import HyprEventsListener


@feature.on_startup
def on_startup():
    HyprEventsListener.start()


@feature.on_shutdown
def on_shutdown():
    HyprEventsListener.stop()


@feature.websocket
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
