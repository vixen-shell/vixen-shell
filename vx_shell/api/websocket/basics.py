import json
from typing import TypedDict, Optional
from fastapi import WebSocket
from pydantic import BaseModel, ConfigDict, ValidationError
from vx_config import VxConfig
from vx_systray import SysTrayState
from vx_logger import Logger
from ..api import api


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


# ---------------------------------------------- - - -
# VIXEN STATE SOCKET
#


class InputStateEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    data: dict = None


@api.websocket("/vx_state")
async def vixen_state_socket(websocket: WebSocket):
    await websocket.accept()

    VxConfig.websockets.append(websocket)
    Logger.log(f'({len(VxConfig.websockets)}) - "WebSocket /vx_state" [connected]')

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
        VxConfig.websockets.remove(websocket)
        Logger.log(
            f'({len(VxConfig.websockets)}) - "WebSocket /vx_state" [disconnected]'
        )


# ---------------------------------------------- - - -
# VIXEN SYSTRAY SOCKET
#


class InputSysTrayEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str


@api.websocket("/vx_systray")
async def vixen_systray_socket(websocket: WebSocket):
    await websocket.accept()

    SysTrayState.websockets.append(websocket)
    Logger.log(
        f'({len(SysTrayState.websockets)}) - "WebSocket /vx_systray" [connected]'
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
        SysTrayState.websockets.remove(websocket)
        Logger.log(
            f'({len(SysTrayState.websockets)}) - "WebSocket /vx_systray" [disconnected]'
        )
