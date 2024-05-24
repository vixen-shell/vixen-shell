import asyncio, json
from typing import TypedDict, Optional
from fastapi import WebSocket
from pydantic import BaseModel, ConfigDict, ValidationError
from ..api import api
from ...features import Features
from ...globals import Models
from ...logger import Logger


def get_feature(feature_name: str):
    feature = Features.get(feature_name)

    if not feature:
        raise Exception(f"Feature '{feature_name}' not found")

    if not feature.is_started:
        raise Exception(f"Feature '{feature_name}' is not started")

    return feature


# ---------------------------------------------- - - -
# FEATURE WEBSOCKET
#


@api.websocket("/feature/{feature_name}/socket/{handler_name}")
async def feature_data_streamer_websocket(
    websocket: WebSocket, feature_name: str, handler_name: str
):
    await websocket.accept()

    try:
        feature = get_feature(feature_name)
    except Exception as exception:
        await websocket.close(reason=str(exception))
        return

    try:
        socket_handler = feature.content.get("socket", handler_name)
    except KeyError as key_error:
        await websocket.close(
            reason=f"{key_error} not found in '{feature_name}' feature websocket handlers"
        )
        return

    await socket_handler(websocket)


# ---------------------------------------------- - - -
# FEATURE STATE WEBSOCKET
#


class OutputEvent(TypedDict):
    id: str
    data: Optional[dict]


class InputEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    data: dict = None


class ErrorEvent(Exception):
    def __init__(self, event: str, message: str, data: dict = {}) -> None:
        super().__init__(message)
        self.event = event
        self.message = message

        data.update({"event": event, "message": message})
        self.data = data


@api.websocket("/feature/{feature_name}/state")
async def feature_state_websocket(websocket: WebSocket, feature_name: str):
    await websocket.accept()

    try:
        feature = get_feature(feature_name)
    except Exception as exception:
        await websocket.close(reason=str(exception))
        return

    if not feature.content.params.state_is_enable:
        await websocket.close(reason=f"'{feature_name}' feature state is disable")
        return

    feature.state_clients.append(websocket)

    async def dispatch_event(event: OutputEvent):
        for websocket in feature.state_clients:
            await websocket.send_json(event)

    try:
        while True:
            try:
                input_event = InputEvent(**await websocket.receive_json())

                if input_event.id == "GET":
                    if not input_event.data:
                        raise ErrorEvent("GET", "Missing item data")

                    key = input_event.data.get("key")
                    if not key:
                        raise ErrorEvent("GET", "Missing item key")

                    if not key in feature.content.params.state:
                        raise ErrorEvent(
                            event="GET",
                            message="Key not found",
                            data={"key": key},
                        )

                    await dispatch_event(
                        OutputEvent(
                            id="UPDATE",
                            data={
                                "key": key,
                                "value": feature.content.params.state[key],
                            },
                        )
                    )

                if input_event.id == "SET":
                    if not input_event.data:
                        raise ErrorEvent("SET", "Missing item data")

                    key = input_event.data.get("key")
                    if not key:
                        raise ErrorEvent("SET", "Missing item key")

                    if not key in feature.content.params.state:
                        raise ErrorEvent(
                            event="SET",
                            message="Key not found",
                            data={"key": key},
                        )

                    feature.content.params.state[key] = input_event.data.get("value")

                    await dispatch_event(
                        OutputEvent(
                            id="UPDATE",
                            data={"key": key, "value": input_event.data.get("value")},
                        )
                    )

                if input_event.id == "SAVE":
                    feature.content.params.save_state()

                    await dispatch_event(
                        OutputEvent(id="SAVE", data=feature.content.params.state)
                    )

            except ErrorEvent as error_event:
                print("Error Event")

                Logger.log(
                    f"[{feature_name}]: (State socket) {error_event.data}",
                    "WARNING",
                )
                await websocket.send_json(
                    OutputEvent(id="ERROR", data=error_event.data)
                )

            except ValidationError as exception:
                print("Validation Error")

                Logger.log(
                    f"[{feature_name}]: (State socket) {str(exception)}",
                    "WARNING",
                )
                await websocket.send_json(
                    OutputEvent(id="ERROR", data=json.loads(exception.json()))
                )

    except:
        feature.state_clients.remove(websocket)


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
                        feature.content.get("data", data_handler.name),
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
