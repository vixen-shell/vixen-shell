import asyncio
from typing import TypedDict, Optional, Callable, Literal, Union
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
from pydantic import BaseModel, ConfigDict
from vx_logger import Logger
from vx_root.root_utils.classes import SocketHandler
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
# FEATURE SOCKETS
#


@api.websocket("/feature/{feature_name}/sockets/{target_feature_name}/{handler_name}")
async def feature_sockets(
    websocket: WebSocket, feature_name: str, target_feature_name: str, handler_name: str
):
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
        target_feature = get_feature(target_feature_name)
    except Exception as exception:
        return await revoke_websocket(exception)

    try:
        handler_func: Callable = target_feature.contents.get("socket", handler_name)
        type_msg_error = "The handler must be a function that returns an instance of class 'SocketHandler'"

        if not callable(handler_func):
            raise TypeError(type_msg_error)

        socket_handler: SocketHandler = handler_func(websocket)

        if not isinstance(socket_handler, SocketHandler):
            raise TypeError(type_msg_error)

    except KeyError as key_error:
        return await revoke_websocket(
            Exception(
                f"{key_error} not found in '{target_feature_name}' feature websocket handlers"
            )
        )

    except TypeError as type_error:
        return await revoke_websocket(type_error)

    except Exception as exception:
        return await revoke_websocket(exception)

    feature.feature_websockets.append(websocket)

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

        feature.feature_websockets.remove(websocket)


# ---------------------------------------------- - - -
# FEATURE DATA STREAMER
#


class IntervalModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interval: float


class DataHandlerModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    args: list = []


class InputDataStreamEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: Literal["SET_INTERVAL", "ADD_HANDLER"]
    data: Union[IntervalModel, DataHandlerModel]


class DataHandler:
    def __init__(self, handler, handler_args: list = []):
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

    feature.feature_websockets.append(websocket)

    data_handlers: dict[str, DataHandler] = {}
    interval: float = 1

    async def stream_loop():
        try:
            while True:
                data = {}
                current_handlers = data_handlers.copy()

                for name, handler in current_handlers.items():
                    data[name] = handler.get_data()

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

                    data_handlers[data_handler.name] = DataHandler(
                        feature.contents.get("data", data_handler.name),
                        data_handler.args,
                    )

            except Exception as exception:
                await websocket.send_json(
                    OutputEvent(
                        id="ERROR",
                        data={"message": str(exception)},
                    )
                )

    except:
        feature.feature_websockets.remove(websocket)
        stream_task.cancel()
