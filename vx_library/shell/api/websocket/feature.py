import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosedOK
from pydantic import BaseModel
from ..api import api
from ...features import Features
from ...globals import Models


# ---------------------------------------------- - - -
# FEATURE PIPE WEBSOCKET
#


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


# ---------------------------------------------- - - -
# CUSTOM DATA STREAMER
#


class DataStreamerInit(BaseModel):
    data_ids: list[str]
    interval: float = 1


@api.websocket("/feature/{feature_name}/custom_data_streamer")
async def feature_pipe_websocket(websocket: WebSocket, feature_name: str):
    feature = Features.get(feature_name)

    if not feature:
        await websocket.close(reason=f"Feature '{feature_name}' not found")

    await websocket.accept()

    try:
        while True:
            try:
                init_data = await websocket.receive_json()
                init = DataStreamerInit(**init_data)

                data_handlers = {}
                for id in init.data_ids:
                    data_handlers[id] = getattr(feature.custom_data, id)

                interval = init.interval

                while True:
                    custom_data = {}

                    for id, data_handler in data_handlers.items():
                        custom_data[id] = data_handler()

                    await websocket.send_json(custom_data)
                    await asyncio.sleep(interval)

            except ValueError as value_error:
                await websocket.send_json(
                    Models.Commons.Error(message=str(value_error)).model_dump()
                )

    except (WebSocketDisconnect, ConnectionClosedOK):
        pass
