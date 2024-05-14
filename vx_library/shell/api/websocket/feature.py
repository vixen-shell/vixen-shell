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
# DATA STREAMER
#


class DataHandlerModel(BaseModel):
    name: str
    args: list = []


class DataStreamerModel(BaseModel):
    data_handlers: list[DataHandlerModel]
    interval: float = 1


class DataHandler:
    def __init__(self, handler, handler_args: list = []):
        self.handler = handler
        self.handler_args = handler_args

    def get_data(self):
        return self.handler(*self.handler_args)


@api.websocket("/feature/{feature_name}/data_streamer")
async def feature_data_streamer_websocket(websocket: WebSocket, feature_name: str):
    await websocket.accept()

    try:
        feature = get_feature(feature_name)
    except Exception as exception:
        await websocket.close(reason=str(exception))
        return

    try:
        while True:
            try:
                init_data = DataStreamerModel(**(await websocket.receive_json()))

                data_handlers: dict[str, DataHandler] = {}
                for data_handler in init_data.data_handlers:
                    data_handlers[data_handler.name] = DataHandler(
                        feature.data_handlers[data_handler.name],
                        data_handler.args,
                    )

                interval = init_data.interval

                while True:
                    data = {}

                    for name, handler in data_handlers.items():
                        data[name] = handler.get_data()

                    await websocket.send_json(data)
                    await asyncio.sleep(interval)

            except KeyError as key_error:
                await websocket.send_json(
                    Models.Commons.Error(
                        message=f"{key_error} not found in '{feature_name}' feature data handlers"
                    ).model_dump()
                )

            except Exception as exception:
                await websocket.send_json(
                    Models.Commons.Error(message=str(exception)).model_dump()
                )

    except:
        pass
