import asyncio, json
from typing import TypedDict, Optional, Callable, Literal, Union
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
from pydantic import BaseModel, ConfigDict, ValidationError
from vx_config import VxConfig
from vx_systray import SysTrayState
from vx_logger import Logger
from vx_root import SocketHandler
from ..api import api
from ...features import Features


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
# FEATURE STATE SOCKET
#


class InputStateEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    data: dict = None


@api.websocket("/feature/{feature_name}/state")
async def vixen_state_socket(websocket: WebSocket, feature_name: str):
    await websocket.accept()

    async def revoke_websocket(e: Exception):
        Logger.log_exception(e)
        await websocket.send_json(OutputEvent(id="ERROR", data={"message": str(e)}))
        await websocket.close(reason=str(e))

    try:
        feature = get_feature(feature_name)
    except Exception as exception:
        return await revoke_websocket(exception)

    feature.attach_websocket("state", websocket)
    Logger.log(
        f'(State WebSockets: {len(VxConfig.websockets)}) - "/feature/{feature_name}/state" [connected]'
    )

    async def dispatch_event(event: OutputEvent):
        for websocket in VxConfig.websockets:
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

                    if not key in VxConfig.STATE:
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
                                "value": VxConfig.STATE[key],
                            },
                        )
                    )

                if input_event.id == "SET":
                    if not input_event.data:
                        raise ErrorEvent("SET", "Missing item data")

                    key = input_event.data.get("key")
                    if not key:
                        raise ErrorEvent("SET", "Missing item key")

                    if not key in VxConfig.STATE:
                        raise ErrorEvent(
                            event="SET",
                            message="Key not found",
                            data={"key": key},
                        )

                    VxConfig.STATE[key] = input_event.data.get("value")

                    await dispatch_event(
                        OutputEvent(
                            id="UPDATE",
                            data={"key": key, "value": input_event.data.get("value")},
                        )
                    )

                if input_event.id == "SAVE":
                    VxConfig.save()
                    await dispatch_event(OutputEvent(id="SAVE", data=VxConfig.STATE))

            except ErrorEvent as error_event:
                Logger.log(
                    f"[State socket]: {error_event.data}",
                    "WARNING",
                )
                await websocket.send_json(
                    OutputEvent(id="ERROR", data=error_event.data)
                )

            except ValidationError as exception:
                Logger.log(
                    f"[State socket]: {str(exception)}",
                    "WARNING",
                )
                await websocket.send_json(
                    OutputEvent(id="ERROR", data=json.loads(exception.json()))
                )

    except:
        await feature.detach_websocket("state", websocket)
        Logger.log(
            f'(State WebSockets: {len(VxConfig.websockets)}) - "/feature/{feature_name}/state" [disconnected]'
        )


# ---------------------------------------------- - - -
# FEATURE SYSTRAY SOCKET
#


class InputSysTrayEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str


@api.websocket("/feature/{feature_name}/systray")
async def vixen_systray_socket(websocket: WebSocket, feature_name: str):
    await websocket.accept()

    async def revoke_websocket(e: Exception):
        Logger.log_exception(e)
        await websocket.send_json(OutputEvent(id="ERROR", data={"message": str(e)}))
        await websocket.close(reason=str(e))

    try:
        feature = get_feature(feature_name)
    except Exception as exception:
        return await revoke_websocket(exception)

    feature.attach_websocket("systray", websocket)
    Logger.log(
        f'(SysTray WebSockets: {len(SysTrayState.websockets)}) - "/feature/{feature_name}/systray" [connected]'
    )

    try:
        while True:
            try:
                input_event = InputSysTrayEvent(**await websocket.receive_json())

                if input_event.id == "UPDATE":
                    await websocket.send_json(
                        {"id": "UPDATE", "data": {"systray": SysTrayState.state}}
                    )
            except ValidationError as exception:
                Logger.log(
                    f"[SysTray socket]: {str(exception)}",
                    "WARNING",
                )
                await websocket.send_json(
                    OutputEvent(id="ERROR", data=json.loads(exception.json()))
                )
    except:
        await feature.detach_websocket("systray", websocket)
        Logger.log(
            f'(SysTray WebSockets: {len(SysTrayState.websockets)}) - "/feature/{feature_name}/systray" [disconnected]'
        )


# ---------------------------------------------- - - -
# FEATURE SOCKETS
#


@api.websocket("/feature/{feature_name}/sockets/{handler_name}")
async def feature_sockets(websocket: WebSocket, feature_name: str, handler_name: str):
    await websocket.accept()

    async def revoke_websocket(e: Exception):
        Logger.log_exception(e)
        await websocket.send_json(OutputEvent(id="ERROR", data={"message": str(e)}))
        await websocket.close(reason=str(e))

    try:
        feature = get_feature(feature_name)
    except Exception as exception:
        return await revoke_websocket(exception)

    try:
        handler_func: Callable = feature.contents.get("socket", handler_name)
        type_msg_error = "The handler must be a function that returns an instance of class 'SocketHandler'"

        if not callable(handler_func):
            raise TypeError(type_msg_error)

        socket_handler: SocketHandler = handler_func(websocket)

        if not isinstance(socket_handler, SocketHandler):
            raise TypeError(type_msg_error)

    except KeyError as key_error:
        return await revoke_websocket(
            Exception(
                f"{key_error} not found in '{feature_name}' feature websocket handlers"
            )
        )

    except TypeError as type_error:
        return await revoke_websocket(type_error)

    except Exception as exception:
        return await revoke_websocket(exception)

    feature.attach_websocket("feature", websocket)
    Logger.log(
        f'(Feature WebSockets: {len(feature.feature_websockets)}) - "/feature/{feature_name}/sockets/{handler_name}" [connected]'
    )

    try:
        try:
            await socket_handler.on_opening()
        except Exception as exception:
            await revoke_websocket(exception)
            raise exception

        while True:
            try:
                await socket_handler.on_loop_iteration()
            except WebSocketDisconnect:
                raise
            except Exception as exception:
                await revoke_websocket(exception)
                raise exception

    except:
        try:
            await socket_handler.on_closing()
        except Exception as exception:
            Logger.log_exception(exception)

        await feature.detach_websocket("feature", websocket)
        Logger.log(
            f'(Feature WebSockets: {len(feature.feature_websockets)}) - "/feature/{feature_name}/sockets/{handler_name}" [disconnected]'
        )


# ---------------------------------------------- - - -
# FEATURE DATA STREAMER
#


class IntervalModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interval: float


class DataHandlerModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data_name: str
    handler_name: str
    handler_args: list = []


class InputDataStreamEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: Literal["SET_INTERVAL", "ADD_HANDLER"]
    data: Union[IntervalModel, DataHandlerModel]


class DataHandler:
    def __init__(self, data_name: str, handler, handler_args: list = []):
        self.data_name = data_name
        self.handler = handler
        self.handler_args = handler_args

    def get_data(self):
        try:
            return self.handler(*self.handler_args)
        except Exception as exception:
            Logger.log_exception(exception)
            raise exception


@api.websocket("/feature/{feature_name}/data_streamer")
async def feature_data_streamer(websocket: WebSocket, feature_name: str):
    await websocket.accept()

    async def revoke_websocket(message: str):
        await websocket.send_json(OutputEvent(id="ERROR", data={"message": message}))
        await websocket.close(reason=message)

    try:
        feature = get_feature(feature_name)
    except Exception as exception:
        return await revoke_websocket(str(exception))

    feature.attach_websocket("feature", websocket)
    Logger.log(
        f'(Feature WebSockets: {len(feature.feature_websockets)}) - "/feature/{feature_name}/data_streamer" [connected]'
    )

    data_handlers: list[DataHandler] = []
    interval: float = 1

    async def stream_loop():
        try:
            while True:
                data = {}
                current_handlers = data_handlers.copy()

                for handler in current_handlers:
                    data[handler.data_name] = handler.get_data()

                await websocket.send_json(OutputEvent(id="UPDATE", data=data))
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            pass
        except:
            raise

    stream_task = asyncio.create_task(stream_loop())

    try:
        while True:
            try:
                input_event = InputDataStreamEvent(**await websocket.receive_json())

                if input_event.id == "SET_INTERVAL":
                    interval = input_event.data.interval

                if input_event.id == "ADD_HANDLER":
                    data_handler = input_event.data

                    data_handlers.append(
                        DataHandler(
                            data_handler.data_name,
                            feature.contents.get("data", data_handler.handler_name),
                            data_handler.handler_args,
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
        await feature.detach_websocket("feature", websocket)
        Logger.log(
            f'(Feature WebSockets: {len(feature.feature_websockets)}) - "/feature/{feature_name}/data_streamer" [disconnected]'
        )
        stream_task.cancel()
