import asyncio
from types import ModuleType
from .parameters import Parameters, FeatureParams
from .FrameHandler import FrameHandler
from .FeaturePipe import FeaturePipe
from .pipe_events import InputEvent
from .FeatureState import FeatureState
from ..logger import Log, Logger


class Feature(FeatureState, FeaturePipe):
    def __init__(
        self, name: str, params: FeatureParams, custom_data_module: ModuleType
    ):
        FeatureState.__init__(self, params)
        FeaturePipe.__init__(self)

        self.name = name
        self.dev_mode = params.dev
        self.frames = FrameHandler(name, params)
        self.custom_data = custom_data_module

        self.is_started = False
        self._listen_logs = False

        if params.start and not params.dev:
            self.start()

    @staticmethod
    def load(entry: str):
        name, params, custom_data_module = Parameters.get(entry)
        return name, Feature(name, params, custom_data_module)

    @property
    def frame_ids(self):
        return self.frames.frame_ids

    @property
    def active_frame_ids(self):
        return self.frames.active_frame_ids

    def start(self):
        if not self.is_started:
            self.open_pipe()
            self.frames.init(self.dev_mode)
            self.is_started = True

    async def stop(self):
        if self.is_started:
            if self.listen_logs:
                self.listen_logs = False

            await self.close_pipe()
            self.frames.cleanup()
            self.is_started = False

    def open_frame(self, frame_id: str):
        if self.is_started:
            new_frame_id = self.frames.open(frame_id)
            return new_frame_id if new_frame_id else frame_id

    def close_frame(self, id: str):
        if self.is_started:
            self.frames.close(id)

    @property
    def listen_logs(self):
        return self._listen_logs

    def _dispatch_log(self, log: Log):
        asyncio.create_task(self.dispatch_event({"id": "LOG", "data": log}))

    @listen_logs.setter
    def listen_logs(self, value: bool):
        if self._listen_logs != value:
            self._listen_logs = value

            if value:
                Logger.add_listener(self._dispatch_log)
            else:
                Logger.remove_listener(self._dispatch_log)

    async def handle_pipe_events(self, event: InputEvent, client_id: str):
        if self.pipe_is_opened:
            await self.handle_state_events(
                event, self.client_websockets[client_id], self.dispatch_event
            )
            await self.handle_log_events(event)

    async def handle_log_events(self, event: InputEvent):
        if event["id"] == "LOG":
            event_data = event.get("data")

            if event_data:
                level = event_data.get("level") or "INFO"
                message = event_data.get("message")

                if message:
                    Logger.log(message, level)