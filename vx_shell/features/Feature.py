import asyncio
from vx_features import (
    ParamDataHandler,
    RootContents,
    RootFeature,
)
from fastapi import WebSocket
from vx_root.root_utils.classes import ContextMenu
from .FrameHandler import FrameHandler
from ..logger import Logger


class Feature:
    @staticmethod
    def load(entry: str, tty_path: str = None):
        from .FeatureLoader import FeatureLoader

        feature_loader = FeatureLoader(entry, tty_path)
        return feature_loader.load()

    def check_is_started(value: bool):
        def decorator(method):
            def wrapper(self, *args, **kwargs):
                if self.is_started == value:
                    return method(self, *args, **kwargs)
                else:
                    raise ValueError(
                        f"[{self.feature_name}]: Feature is not started"
                        if value
                        else f"[{self.feature_name}]: Feature is already started"
                    )

            return wrapper

        return decorator

    def __init__(self, feature_name: str, dev_mode: bool):
        self.feature_name = feature_name
        self.dev_mode = dev_mode
        # -------------------------------------------- - - -
        self.contents = RootContents(feature_name)
        self.required_features = RootFeature(feature_name).required_features
        self.lifespan = RootFeature(feature_name).lifespan
        # -------------------------------------------- - - -
        # self.state_websockets: list[WebSocket] = []
        self.feature_websockets: list[WebSocket] = []
        self.frames = FrameHandler(feature_name=feature_name)
        self.is_started = False
        # -------------------------------------------- - - -
        if (
            ParamDataHandler.get_value(f"{feature_name}.autostart")
            and not self.dev_mode
        ):
            self.start()

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
            if self.required_features:
                from .Features import Features

                def get_expected_deps():
                    deps: list[str] = self.required_features.copy()

                    for dep_name in self.required_features:
                        dep_feature = Features.get(dep_name)

                        if bool(dep_feature and dep_feature.is_started):
                            if dep_name in deps:
                                deps.remove(dep_name)

                    return deps

                expected_deps = get_expected_deps()

                if expected_deps:
                    Logger.log(f"[{self.feature_name}]: await {expected_deps}")

                while expected_deps:
                    check_deps = get_expected_deps()

                    if check_deps != expected_deps:
                        expected_deps = check_deps

                        if expected_deps:
                            Logger.log(f"[{self.feature_name}]: await {expected_deps}")

                    await asyncio.sleep(0.5)

            try:
                startup = self.lifespan.startup_sequence()
            except Exception as exception:
                Logger.log_exception(exception)

            if startup == True:
                self.frames.init(self.dev_mode)
                self.is_started = True
                Logger.log(f"[{self.feature_name}]: feature started")
            else:
                Logger.log(
                    f"[{self.feature_name}]: startup sequence return 'False'. "
                    "Unable to start feature!",
                    "WARNING",
                )

        asyncio.create_task(process())

    @check_is_started(True)
    async def stop(self) -> bool:
        try:
            if self.lifespan.shutdown_sequence() == False:
                Logger.log(
                    f"[{self.feature_name}]: shutdown sequence return 'False'!",
                    "WARNING",
                )
        except Exception as exception:
            Logger.log_exception(exception)

        # state_websockets = self.state_websockets.copy()
        # for websocket in state_websockets:
        #     await websocket.close()

        feature_websockets = self.feature_websockets.copy()
        for websocket in feature_websockets:
            await websocket.close()

        self.frames.cleanup()

        self.is_started = False
        Logger.log(f"[{self.feature_name}]: feature stopped")

    @check_is_started(True)
    def open_frame(self, frame_id: str):
        new_frame_id = self.frames.open(frame_id)
        return new_frame_id if new_frame_id else frame_id

    @check_is_started(True)
    def close_frame(self, id: str):
        self.frames.close(id)

    @check_is_started(True)
    def popup_context_menu(self, frame_id: str, context_menu: ContextMenu):
        self.frames.popup_context_menu(frame_id, context_menu)
