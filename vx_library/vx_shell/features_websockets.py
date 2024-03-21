from fastapi import WebSocket
from .api import api
from .features import Features


@api.websocket("/feature/{feature_name}/pipe/{client_id}")
async def feature_pipe_websocket(
    websocket: WebSocket, feature_name: str, client_id: str
):
    feature = await Features.connect_client(feature_name, client_id, websocket)

    if feature:
        try:
            while True:
                await feature.handle_pipe_events(
                    await websocket.receive_json(), client_id
                )
        except:
            feature.remove_client(client_id)
