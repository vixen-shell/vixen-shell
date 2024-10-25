import asyncio
from typing import Literal
from vx_features import (
    ParamDataHandler,
    RootContents,
    RootFeature,
)
from fastapi import WebSocket
from vx_config import VxConfig
from vx_systray import SysTrayState
from vx_gtk import Gtk
from vx_logger import Logger
from .FrameHandler import FrameHandler


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

    def check_is_active(value: bool):
        def decorator(method):
            def wrapper(self, *args, **kwargs):
                if bool(self.is_active or self.is_started) == value:
                    return method(self, *args, **kwargs)
                else:
                    raise ValueError(
                        f"[{self.feature_name}]: Feature is not started"
                        if value
                        else f"[{self.feature_name}]: Feature is already {'started' if self.is_started else 'waiting to start'}"
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
        self.feature_websockets: list[WebSocket] = []
        self.state_websockets: list[WebSocket] = []
        self.systray_websockets: list[WebSocket] = []
        # -------------------------------------------- - - -
        self.frames = FrameHandler(feature_name=feature_name)
        self.is_active = False
        self.is_started = False
        # -------------------------------------------- - - -
        if (
            ParamDataHandler.get_value(f"{feature_name}.autostart")
            and not self.dev_mode
        ):
            self.start()

    @check_is_started(True)
    def attach_websocket(
        self, type: Literal["feature", "state", "systray"], websocket: WebSocket
    ):
        websockets: list[WebSocket] = getattr(self, f"{type}_websockets")
        websockets.append(websocket)

        if type == "state":
            VxConfig.websockets.append(websocket)

        if type == "systray":
            SysTrayState.websockets.append(websocket)

    @check_is_started(True)
    async def detach_websocket(
        self, type: Literal["feature", "state", "systray"], websocket: WebSocket
    ):
        try:
            await websocket.close()
        except:
            pass

        websockets: list[WebSocket] = getattr(self, f"{type}_websockets")
        websockets.remove(websocket)

        if type == "state":
            VxConfig.websockets.remove(websocket)

        if type == "systray":
            SysTrayState.websockets.remove(websocket)

    @check_is_started(True)
    async def cleanup_websockets(self):
        async def close_websockets(websockets: list[WebSocket]):
            for websocket in websockets:
                try:
                    await websocket.close()
                except:
                    pass

        await close_websockets(self.feature_websockets.copy())
        await close_websockets(self.state_websockets.copy())
        await close_websockets(self.systray_websockets.copy())

        for websocket in self.state_websockets:
            VxConfig.websockets.remove(websocket)

        for websocket in self.systray_websockets:
            SysTrayState.websockets.remove(websocket)

    async def startup_handler(self):
        from .Features import Features

        Logger.log(
            f"[{self.feature_name}]: waiting for required features {self.required_features}"
        )

        def feature_is_started(feature_name: str):
            def is_started():
                feature = Features.get(feature_name)
                return bool(feature and feature.is_started)

            return is_started

        required_features_state = [
            feature_is_started(feature_name) for feature_name in self.required_features
        ]

        while self.is_active:
            required_features_are_started = all(f() for f in required_features_state)

            if not required_features_are_started and self.is_started:
                Logger.log(f"[{self.feature_name}]: waiting for required features")
                await self.__stop()

            if required_features_are_started and not self.is_started:
                Logger.log(f"[{self.feature_name}]: required features satisfied")
                self.__start()

            await asyncio.sleep(0.5)

        if self.is_started:
            await self.__stop()

    @check_is_active(False)
    def start(self):
        if self.required_features:
            self.is_active = True
            asyncio.create_task(self.startup_handler())
        else:
            self.__start()

    @check_is_active(True)
    async def stop(self):
        if self.is_active:
            self.is_active = False
        else:
            await self.__stop()

    @check_is_started(False)
    def __start(self):
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

    @check_is_started(True)
    async def __stop(self) -> bool:
        try:
            if self.lifespan.shutdown_sequence() == False:
                Logger.log(
                    f"[{self.feature_name}]: shutdown sequence return 'False'!",
                    "WARNING",
                )
        except Exception as exception:
            Logger.log_exception(exception)

        await self.cleanup_websockets()
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
    def popup_context_menu(self, frame_id: str, menu: Gtk.Menu):
        self.frames.popup_context_menu(frame_id, menu)

    @check_is_started(True)
    def popup_dbus_menu(self, frame_id: str, service_name: str):
        self.frames.popup_dbus_menu(frame_id, service_name)

    @property
    @check_is_started(True)
    def frame_ids(self):
        return self.frames.frame_ids

    @property
    @check_is_started(True)
    def active_frame_ids(self):
        return self.frames.active_frame_ids
