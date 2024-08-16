import os, asyncio
from typing import Callable
from vx_features import (
    RootModule,
    RootFeature,
    RootUtils,
    ParamDataHandler,
    ParamData,
    ParamsValueError,
    root_FeatureParams_dict,
    FeatureSharedContent,
    FeatureContentType,
    FeatureLifespan,
    is_dev_feature,
    get_feature_references,
)
from fastapi import WebSocket
from .FrameHandler import FrameHandler
from .Gtk_dialog import show_dialog_box
from ..logger import Logger

USER_PARAMS_DIRECTORY = f"{os.path.expanduser('~')}/.config/vixen/features"


class Feature:
    @staticmethod
    def load(entry: str, tty_path: str = None):
        RootModule(entry)
        feature = Feature(entry, tty_path)

        return feature.feature_name, feature

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

    def __init__(self, entry: str, tty_path: str = None):
        self.__init_root(entry)
        self.tty_path: str = tty_path
        self.dev_mode: bool = is_dev_feature(entry)
        self.__init_params(entry)

        # -------------------------------------------- - - -
        self.state_websockets: list[WebSocket] = []
        self.feature_websockets: list[WebSocket] = []
        self.frames = FrameHandler(feature_name=self.feature_name)
        self.is_started = False

        # -------------------------------------------- - - -
        if (
            ParamDataHandler.get_value(f"{self.feature_name}.autostart")
            and not self.dev_mode
        ):
            self.start()

    def __init_root(self, entry: str):
        root_feature = RootFeature(entry)
        root_utils = RootUtils(entry)

        self.feature_name: str = None
        self.root_params: root_FeatureParams_dict = None
        self.required_features: list[str] = None
        self.shared_content: FeatureSharedContent = None
        self.lifespan: FeatureLifespan = None

        self.__dict__ = {
            key.removeprefix("_RootFeature__"): root_feature.__dict__[key]
            for key in root_feature.__dict__
            if key.startswith("_RootFeature__")
        }

        root_feature.current = get_feature_references(self)

        from .Features import Features

        root_utils.init(Logger, Features, show_dialog_box)

    def __init_params(self, entry: str):
        user_params_filepath = (
            f"{entry}/user/{self.feature_name}.json"
            if self.dev_mode
            else f"{USER_PARAMS_DIRECTORY}/{self.feature_name}.json"
        )

        try:
            ParamDataHandler.add_param_data(
                feature_name=self.feature_name,
                param_data=ParamData(
                    root_params_dict=self.root_params,
                    user_params_filepath=user_params_filepath,
                    dev_mode=self.dev_mode,
                ),
            )

        except ParamsValueError as param_error:
            raise Exception(f"[{self.feature_name}]: {str(param_error)}")

    @property
    @check_is_started(True)
    def frame_ids(self):
        return self.frames.frame_ids

    @property
    @check_is_started(True)
    def active_frame_ids(self):
        return self.frames.active_frame_ids

    @check_is_started(True)
    def get_shared_content(self, content_type: FeatureContentType, handler_name: str):
        sub_contents: dict[str, Callable] = getattr(self.shared_content, content_type)
        return sub_contents[handler_name]

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
                self.lifespan.startup()
            except Exception as exception:
                Logger.log_exception(exception)

            self.frames.init(self.dev_mode)
            self.is_started = True
            Logger.log(f"[{self.feature_name}]: feature started")

        asyncio.create_task(process())

    @check_is_started(True)
    async def stop(self):
        try:
            self.lifespan.shutdown()
        except Exception as exception:
            Logger.log_exception(exception)

        state_websockets = self.state_websockets.copy()
        for websocket in state_websockets:
            await websocket.close()

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
