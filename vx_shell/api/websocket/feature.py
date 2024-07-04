import asyncio, json
from typing import TypedDict, Optional
from fastapi import WebSocket
from pydantic import BaseModel, ConfigDict, ValidationError
from vx_feature_utils import ParamDataHandler
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


@api.websocket("/feature/{feature_name}/sockets/{target_feature_name}/{handler_name}")
async def feature_sockets(
    websocket: WebSocket, feature_name: str, target_feature_name: str, handler_name: str
):
    await websocket.accept()

    async def revoke_websocket(message: str):
        await websocket.send_json(OutputEvent(id="ERROR", data={"message": message}))
        await websocket.close(reason=message)

    try:
        feature = get_feature(feature_name)
    except Exception as exception:
        return await revoke_websocket(str(exception))

    try:
        target_feature = get_feature(target_feature_name)
    except Exception as exception:
        return await revoke_websocket(str(exception))

    try:
        socket_handler = target_feature.content.get("socket", handler_name)
        on_open, loop_content, on_close = socket_handler(websocket)
    except KeyError as key_error:
        return await revoke_websocket(
            f"{key_error} not found in '{target_feature_name}' feature websocket handlers"
        )

    feature.websockets.append(websocket)

    try:
        if on_open:
            await on_open()

        while True:
            if loop_content:
                await loop_content()
            else:
                await websocket.receive_text()

    except:
        if on_close:
            await on_close()

        feature.websockets.remove(websocket)


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

    async def revoke_websocket(message: str):
        await websocket.send_json(OutputEvent(id="ERROR", data={"message": message}))
        await websocket.close(reason=message)

    try:
        feature = get_feature(feature_name)
    except Exception as exception:
        return await revoke_websocket(str(exception))

    if not ParamDataHandler.state_is_enable(feature_name):
        return await revoke_websocket(f"'{feature_name}' feature state is disable")

    feature.state_websockets.append(websocket)
    feature_state = ParamDataHandler.get_state(feature_name)

    async def dispatch_event(event: OutputEvent):
        for websocket in feature.state_websockets:
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

                    if not key in feature_state:
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
                                "value": feature_state[key],
                            },
                        )
                    )

                if input_event.id == "SET":
                    if not input_event.data:
                        raise ErrorEvent("SET", "Missing item data")

                    key = input_event.data.get("key")
                    if not key:
                        raise ErrorEvent("SET", "Missing item key")

                    if not key in feature_state:
                        raise ErrorEvent(
                            event="SET",
                            message="Key not found",
                            data={"key": key},
                        )

                    feature_state[key] = input_event.data.get("value")

                    await dispatch_event(
                        OutputEvent(
                            id="UPDATE",
                            data={"key": key, "value": input_event.data.get("value")},
                        )
                    )

                if input_event.id == "SAVE":
                    ParamDataHandler.save_params(feature_name)

                    await dispatch_event(OutputEvent(id="SAVE", data=feature_state))

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
        feature.state_websockets.remove(websocket)


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


@api.websocket("/feature/{feature_name}/data_streamer/{target_feature_name}")
async def feature_data_streamer(
    websocket: WebSocket, feature_name: str, target_feature_name: str
):
    await websocket.accept()

    async def revoke_websocket(message: str):
        await websocket.send_json(OutputEvent(id="ERROR", data={"message": message}))
        await websocket.close(reason=message)

    try:
        feature = get_feature(feature_name)
    except Exception as exception:
        return await revoke_websocket(str(exception))

    try:
        target_feature = get_feature(target_feature_name)
    except Exception as exception:
        return await revoke_websocket(str(exception))

    feature.websockets.append(websocket)

    try:
        while True:
            try:
                input_event = InputDataStreamEvent(**await websocket.receive_json())

                if input_event.id == "INIT":
                    init_data = input_event.data

                    data_handlers: dict[str, DataHandler] = {}
                    for data_handler in init_data.data_handlers:
                        data_handlers[data_handler.name] = DataHandler(
                            target_feature.content.get("data", data_handler.name),
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
                            "message": f"{key_error} not found in '{target_feature_name}' feature data handlers"
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
        feature.websockets.remove(websocket)
