import asyncio
from vx_feature_utils import Utils
from fastapi import WebSocket
from .FrameHandler import FrameHandler
from .Gtk_dialog import show_dialog_box
from ..logger import Logger


class Feature:
    @staticmethod
    def load(entry: str):
        content, utils = Utils.get_feature_content(entry)
        content.init_params(entry)

        feature = Feature(content)

        if utils:
            from .Features import Features

            utils.init(Logger, feature, Features, show_dialog_box)

        if content.params.autostart and not content.dev_mode:
            feature.start()

        return content.feature_name, feature

    def check_is_started(value: bool):
        def decorator(method):
            def wrapper(self, *args, **kwargs):
                if self.is_started == value:
                    return method(self, *args, **kwargs)
                else:
                    raise ValueError(
                        f"[{self.content.feature_name}]: Feature is not started"
                        if value
                        else f"[{self.content.feature_name}]: Feature is already started"
                    )

            return wrapper

        return decorator

    def __init__(self, content: Utils.FeatureContent):
        self.content = content
        self.state_websockets: list[WebSocket] = []
        self.websockets: list[WebSocket] = []

        self.frames = FrameHandler(
            feature_name=content.feature_name,
            feature_params=content.params,
        )

        self.is_started = False

    @property
    @check_is_started(True)
    def frame_ids(self):
        return self.frames.frame_ids

    @property
    @check_is_started(True)
    def active_frame_ids(self):
        return self.frames.active_frame_ids

    @check_is_started(False)
    def start(self):
        async def process():
            if self.content.start_after:
                from .Features import Features

                def get_expected_deps():
                    deps: list[str] = self.content.start_after.copy()

                    for dep_name in self.content.start_after:
                        dep_feature = Features.get(dep_name)

                        if bool(dep_feature and dep_feature.is_started):
                            if dep_name in deps:
                                deps.remove(dep_name)

                    return deps

                expected_deps = get_expected_deps()

                if expected_deps:
                    Logger.log(f"[{self.content.feature_name}]: await {expected_deps}")

                while expected_deps:
                    check_deps = get_expected_deps()

                    if check_deps != expected_deps:
                        expected_deps = check_deps

                        if expected_deps:
                            Logger.log(
                                f"[{self.content.feature_name}]: await {expected_deps}"
                            )

                    await asyncio.sleep(0.5)

            self.content.startup_sequence()
            self.frames.init(self.content.dev_mode)
            self.is_started = True
            Logger.log(f"[{self.content.feature_name}]: feature started")

        asyncio.create_task(process())

    @check_is_started(True)
    async def stop(self):
        self.content.shutdown_sequence()

        for websocket in self.state_websockets:
            await websocket.close()

        for websocket in self.websockets:
            await websocket.close()

        self.frames.cleanup()

        self.is_started = False
        Logger.log(f"[{self.content.feature_name}]: feature stopped")

    @check_is_started(True)
    def open_frame(self, frame_id: str):
        new_frame_id = self.frames.open(frame_id)
        return new_frame_id if new_frame_id else frame_id

    @check_is_started(True)
    def close_frame(self, id: str):
        self.frames.close(id)
