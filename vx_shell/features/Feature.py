import asyncio, os, json
from typing import TypedDict, Optional, Literal
from vx_features import ParamDataHandler, RootContents
from fastapi import WebSocket
from vx_config import VxConfig
from vx_systray import SysTrayState
from vx_gtk import Gtk
from vx_logger import Logger
from vx_types import LifeCycleHandler, LifeCycleCleanUpHandler, user_FrameParams_dict
from vx_gtk.FrameHandler import FrameHandler
from .. import AsyncLoop


class OutputEvent(TypedDict):
    id: str
    data: Optional[dict]


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

        locales_file_path = (
            f"{ParamDataHandler.get_user_dir(self.feature_name)}"
            f"/{self.feature_name}_{VxConfig.locale()}.json"
        )
        locales: dict = {}

        if os.path.exists(locales_file_path):
            with open(locales_file_path, "r", encoding="utf-8") as file:
                locales = json.load(file)

        self.contents.dispatch("data", "__locales__")(lambda: locales)
        # -------------------------------------------- - - -
        self.feature_websockets: list[WebSocket] = []
        self.state_websockets: list[WebSocket] = []
        self.frames_websockets: list[WebSocket] = []
        self.systray_websockets: list[WebSocket] = []
        # -------------------------------------------- - - -
        self.is_active = False
        self.is_started = False
        # -------------------------------------------- - - -
        self.waited_features: list[str] = list(
            ParamDataHandler.get_value(f"{feature_name}.wait_startup") or tuple()
        )
        self.startup_handler: LifeCycleHandler = ParamDataHandler.get_value(
            f"{feature_name}.life_cycle"
        )
        self.cleanup_handler: LifeCycleCleanUpHandler = None

        if (
            ParamDataHandler.get_value(f"{feature_name}.autostart")
            and not self.dev_mode
        ):
            self.start()

    @check_is_started(True)
    def attach_websocket(
        self,
        type: Literal["feature", "state", "frames", "systray"],
        websocket: WebSocket,
    ):
        websockets: list[WebSocket] = getattr(self, f"{type}_websockets")
        websockets.append(websocket)

        if type == "state":
            VxConfig.websockets.append(websocket)

        if type == "systray":
            SysTrayState.websockets.append(websocket)

    @check_is_started(True)
    async def detach_websocket(
        self,
        type: Literal["feature", "state", "frames", "systray"],
        websocket: WebSocket,
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
        await close_websockets(self.frames_websockets.copy())
        await close_websockets(self.systray_websockets.copy())

        for websocket in self.state_websockets:
            VxConfig.websockets.remove(websocket)

        for websocket in self.systray_websockets:
            SysTrayState.websockets.remove(websocket)

        self.feature_websockets = []
        self.state_websockets = []
        self.frames_websockets = []
        self.systray_websockets = []

    async def startup_wait_handler(self):
        from .Features import Features

        Logger.log(
            f"[{self.feature_name}]: waiting for required features {self.waited_features}"
        )

        def feature_is_started(feature_name: str):
            def is_started():
                feature = Features.get(feature_name)
                return bool(feature and feature.is_started)

            return is_started

        required_features_state = [
            feature_is_started(feature_name) for feature_name in self.waited_features
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

    def handle_lifecycle(self, event: Literal["startup", "cleanup"]) -> bool:
        if event == "startup" and self.startup_handler:
            startup = True

            try:
                cleanup_handler = self.startup_handler()

                if callable(cleanup_handler):
                    self.cleanup_handler = cleanup_handler
                elif cleanup_handler == False:
                    Logger.log(
                        f"[{self.feature_name}]: startup sequence return 'False'",
                        "WARNING",
                    )
                    startup = False

            except Exception as exception:
                Logger.log_exception(exception)
                startup = False

            return startup

        if event == "cleanup" and self.cleanup_handler:
            try:
                self.cleanup_handler()
            except Exception as exception:
                Logger.log_exception(exception)

        return True

    @check_is_active(False)
    def start(self):
        if self.waited_features:
            self.is_active = True
            asyncio.create_task(self.startup_wait_handler())
        else:
            self.__start()

    @check_is_active(True)
    async def stop(self, cleanup_frame: bool = True):
        if self.is_active:
            self.is_active = False
        else:
            await self.__stop(cleanup_frame)

    @check_is_started(False)
    def __start(self):
        FrameHandler.init_feature(self.feature_name, self.dev_mode)
        startup = self.handle_lifecycle("startup")

        if startup == True:
            self.is_started = True
            Logger.log(f"[{self.feature_name}]: feature started")

    @check_is_started(True)
    async def __stop(self, cleanup: bool = True) -> bool:
        await self.cleanup_websockets()

        if cleanup:
            FrameHandler.cleanup(self.feature_name)

        self.handle_lifecycle("cleanup")

        self.is_started = False
        Logger.log(f"[{self.feature_name}]: feature stopped")

    # ---------------------------------------------- - - -
    # FRAMES
    #

    async def dispatch_frame_event(self, event: OutputEvent):
        for websocket in self.frames_websockets:
            await websocket.send_json(event)

    @check_is_started(True)
    def open_frame(self, frame_id: str):
        if not frame_id in self.frame_ids:
            raise ValueError(f"Frame ID '{frame_id}' does not exist")

        if frame_id in self.active_frame_ids:
            raise ValueError(f"Frame '{frame_id}' is already open")

        FrameHandler.open(
            self.feature_name,
            frame_id,
            after_open=lambda active_frame_ids: AsyncLoop.run_task(
                self.dispatch_frame_event(
                    OutputEvent(
                        id="OPEN",
                        data={
                            "frame_id": frame_id,
                            "active_frame_ids": active_frame_ids,
                        },
                    )
                )
            ),
        )

        return frame_id

    @check_is_started(True)
    def close_frame(self, frame_id: str):
        if not frame_id in self.frame_ids:
            raise ValueError(f"Frame ID '{frame_id}' does not exist")

        if not frame_id in self.active_frame_ids:
            raise ValueError(f"Frame '{frame_id}' is not open")

        FrameHandler.close(
            self.feature_name,
            frame_id,
            after_close=lambda active_frame_ids: AsyncLoop.run_task(
                self.dispatch_frame_event(
                    OutputEvent(
                        id="CLOSE",
                        data={
                            "frame_id": frame_id,
                            "active_frame_ids": active_frame_ids,
                        },
                    )
                )
            ),
        )

    # @check_is_started(True)
    def new_frame_from_template(
        self, frame_id: str, frame_params_dict: user_FrameParams_dict
    ) -> bool:
        result = FrameHandler.new_frame_from_template(
            self.feature_name, frame_id, frame_params_dict
        )

        if result and self.is_started:
            asyncio.create_task(
                self.dispatch_frame_event(
                    OutputEvent(
                        id="NEW_FROM_TEMPLATE",
                        data={
                            "frame_id": frame_id,
                            "frame_ids": self.frame_ids,
                        },
                    )
                )
            )

        return result

    @check_is_started(True)
    def remove_frame_from_template(self, frame_id: str) -> bool:
        result = FrameHandler.remove_frame_from_template(self.feature_name, frame_id)

        if result:
            asyncio.create_task(
                self.dispatch_frame_event(
                    OutputEvent(
                        id="REMOVE_FROM_TEMPLATE",
                        data={
                            "frame_id": frame_id,
                            "frame_ids": self.frame_ids,
                        },
                    )
                )
            )

        return result

    @property
    @check_is_started(True)
    def frame_ids(self):
        return FrameHandler.frame_ids(self.feature_name)

    @property
    @check_is_started(True)
    def active_frame_ids(self):
        return FrameHandler.active_frame_ids(self.feature_name)

    # ---------------------------------------------- - - -
    # POPUP MENU
    #

    @check_is_started(True)
    def popup_context_menu(self, frame_id: str, menu: Gtk.Menu):
        FrameHandler.popup_context_menu(self.feature_name, frame_id, menu)

    @check_is_started(True)
    def popup_dbus_menu(self, frame_id: str, service_name: str):
        FrameHandler.popup_dbus_menu(self.feature_name, frame_id, service_name)
