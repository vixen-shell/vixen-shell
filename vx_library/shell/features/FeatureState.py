from vx_feature_utils import FeatureParams
from typing import Callable, Coroutine, Any
from fastapi import WebSocket
from .pipe_events import InputEvent, OutputEvent

Dispatcher = Callable[[OutputEvent, str | None], Coroutine[Any, Any, None]]


class FeatureState:
    def __init__(self, feature_params: FeatureParams):
        self.feature_params = feature_params
        self.state = self.feature_params.state or {}

    def save_state(self):
        self.feature_params.state = self.state
        self.feature_params.save()

    async def handle_state_events(
        self, event: InputEvent, client_websocket: WebSocket, dispatcher: Dispatcher
    ):
        event_data = event.get("data")

        async def handle_get():
            if event_data:
                if "key" in event_data:
                    key = event_data["key"]

                    await client_websocket.send_json(
                        OutputEvent(
                            id="UPDATE_STATE",
                            data={"key": key, "value": self.state[key]},
                        )
                    )

        async def handle_set():
            if event_data:
                if "key" in event_data:
                    key = event_data["key"]
                    value = event_data.get("value")

                    self.state[key] = value

                    await dispatcher(
                        OutputEvent(
                            id="UPDATE_STATE", data={"key": key, "value": value}
                        )
                    )

        event_id = event["id"]

        if event_id == "GET_STATE":
            await handle_get()
        if event_id == "SET_STATE":
            await handle_set()
        if event_id == "SAVE_STATE":
            self.save_state()
