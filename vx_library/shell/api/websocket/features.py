from fastapi import WebSocket
from ..api import api
from ...features import Features


@api.websocket("/feature/{feature_name}/pipe/{client_id}")
async def feature_pipe_websocket(
    websocket: WebSocket, feature_name: str, client_id: str
):
    feature = Features.get(feature_name)

    if not feature:
        await websocket.close(reason=f"Feature '{feature_name}' not found")

    if not feature.pipe_is_opened:
        await websocket.close(reason=f"'{feature_name}' feature pipe is closed")

    await feature.connect_client(client_id, websocket)

    try:
        while True:
            await feature.handle_pipe_events(await websocket.receive_json(), client_id)
    except:
        feature.remove_client(client_id)
