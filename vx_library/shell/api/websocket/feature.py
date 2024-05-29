import asyncio, json
from typing import TypedDict, Optional
from fastapi import WebSocket
from pydantic import BaseModel, ConfigDict, ValidationError
from ..api import api
from ...features import Features
from ...logger import Logger


class OutputEvent(TypedDict):
    id: str
    data: Optional[dict]


class ErrorEvent(Exception):
    def __init__(self, event: str, message: str, data: dict = {}) -> None:
        super().__init__(message)
        self.event = event
        self.message = message

        data.update({"event": event, "message": message})
        self.data = data


def get_feature(feature_name: str):
    feature = Features.get(feature_name)

    if not feature:
        raise Exception(f"Feature '{feature_name}' not found")

    if not feature.is_started:
        raise Exception(f"Feature '{feature_name}' is not started")

    return feature


# ---------------------------------------------- - - -
# FEATURE SOCKETS
#


@api.websocket("/feature/{feature_name}/sockets/{handler_name}")
async def feature_sockets(websocket: WebSocket, feature_name: str, handler_name: str):
    await websocket.accept()
    error = None

    try:
        feature = get_feature(feature_name)
    except Exception as exception:
        error = str(exception)

    try:
        socket_handler = feature.content.get("socket", handler_name)
    except KeyError as key_error:
        error = f"{key_error} not found in '{feature_name}' feature websocket handlers"

    if error:
        await websocket.send_json(OutputEvent(id="ERROR", data={"message": error}))
        await websocket.close(reason=error)
        return

    await socket_handler(websocket)


# ---------------------------------------------- - - -
# FEATURE STATE SOCKET
#


class InputStateEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    data: dict = None


@api.websocket("/feature/{feature_name}/state")
async def feature_state_socket(websocket: WebSocket, feature_name: str):
    await websocket.accept()
    error = None

    try:
        feature = get_feature(feature_name)
    except Exception as exception:
        error = str(exception)

    if not feature.content.params.state_is_enable:
        error = f"'{feature_name}' feature state is disable"

    if error:
        await websocket.send_json(OutputEvent(id="ERROR", data={"message": error}))
        await websocket.close(reason=error)
        return

    feature.state_clients.append(websocket)

    async def dispatch_event(event: OutputEvent):
        for websocket in feature.state_clients:
            await websocket.send_json(event)

    try:
        while True:
            try:
                input_event = InputStateEvent(**await websocket.receive_json())

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
                Logger.log(
                    f"[{feature_name}]: (State socket) {error_event.data}",
                    "WARNING",
                )
                await websocket.send_json(
                    OutputEvent(id="ERROR", data=error_event.data)
                )

            except ValidationError as exception:
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
# FEATURE DATA STREAMER
#


class DataHandlerModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    args: list = []


class DataStreamerModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data_handlers: list[DataHandlerModel]
    interval: float = 1


class InputDataStreamEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    data: DataStreamerModel


class DataHandler:
    def __init__(self, handler, handler_args: list = []):
        self.handler = handler
        self.handler_args = handler_args

    def get_data(self):
        return self.handler(*self.handler_args)


@api.websocket("/feature/{feature_name}/data_streamer")
async def feature_data_streamer(websocket: WebSocket, feature_name: str):
    await websocket.accept()
    error = None

    try:
        feature = get_feature(feature_name)
    except Exception as exception:
        error = str(exception)

    if error:
        await websocket.send_json(OutputEvent(id="ERROR", data={"message": error}))
        await websocket.close(reason=error)
        return

    try:
        while True:
            try:
                input_event = InputDataStreamEvent(**await websocket.receive_json())

                if input_event.id == "INIT":
                    init_data = input_event.data

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

                        await websocket.send_json(OutputEvent(id="UPDATE", data=data))
                        await asyncio.sleep(interval)

            except KeyError as key_error:
                await websocket.send_json(
                    OutputEvent(
                        id="ERROR",
                        data={
                            "message": f"{key_error} not found in '{feature_name}' feature data handlers"
                        },
                    )
                )

            except Exception as exception:
                await websocket.send_json(
                    OutputEvent(
                        id="ERROR",
                        data={"message": str(exception)},
                    )
                )

    except:
        pass
