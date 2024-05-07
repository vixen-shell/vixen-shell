import asyncio
from fastapi import WebSocket
from pydantic import BaseModel
from ..api import api
from ...features import Features
from ...globals import Models


def get_feature(feature_name: str):
    feature = Features.get(feature_name)

    if not feature:
        raise Exception(f"Feature '{feature_name}' not found")

    if not feature.is_started:
        raise Exception(f"Feature '{feature.name}' is not started")

    return feature


# ---------------------------------------------- - - -
# FEATURE PIPE WEBSOCKET
#


@api.websocket("/feature/{feature_name}/pipe/{client_id}")
async def feature_pipe_websocket(
    websocket: WebSocket, feature_name: str, client_id: str
):
    await websocket.accept()

    try:
        feature = get_feature(feature_name)
    except Exception as exception:
        await websocket.close(reason=str(exception))
        return

    try:
        await feature.connect_client(client_id, websocket)
    except Exception as exception:
        await websocket.close(reason=str(exception))
        return

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
    await websocket.accept()

    try:
        feature = get_feature(feature_name)
    except Exception as exception:
        await websocket.close(reason=str(exception))
        return

    if not feature.custom_data:
        await websocket.close(
            reason=f"Feature '{feature_name}' does not have a custom data module"
        )
        return

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

            except AttributeError as attribute_error:
                await websocket.send_json(
                    Models.Commons.Error(message=str(attribute_error)).model_dump()
                )

            except ValueError as value_error:
                await websocket.send_json(
                    Models.Commons.Error(message=str(value_error)).model_dump()
                )

    except:
        pass
