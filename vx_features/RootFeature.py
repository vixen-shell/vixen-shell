from typing import Literal, Callable, Any
from vx_root import SocketHandler
from vx_root.references.AbsFrames import AbsFrames
from vx_root.references.AbsParams import AbsParams
from vx_root.references.AbsLogger import AbsLogger
from .params import root_FeatureParams_dict
from .utils import FeatureUtils

FeatureContentType = Literal["action", "data", "file", "socket"]


class FeatureSharedContent:
    def __init__(self):
        self.action: dict[str, Callable[[], None]] = {}
        self.data: dict[str, Callable[[], Any]] = {}
        self.file: dict[str, Callable[[], str]] = {}
        self.socket: dict[str, Callable[[], SocketHandler]] = {}


class FeatureLifespan:
    def __init__(self):
        self.startup_callback: Callable[[], None] | None = None
        self.shutdown_callback: Callable[[], None] | None = None

    def startup_sequence(self):
        if self.startup_callback:
            self.startup_callback()

    def shutdown_sequence(self):
        if self.shutdown_callback:
            self.shutdown_callback()


class RootFeature:
    _instances = {}

    @classmethod
    def del_instance(cls, entry: str):
        feature_name = FeatureUtils.feature_name_from(entry)

        if feature_name in cls._instances:
            del cls._instances[feature_name]

    def __new__(cls, entry: str):
        feature_name = FeatureUtils.feature_name_from(entry)

        if feature_name not in cls._instances:
            cls._instances[feature_name] = super().__new__(cls)

        return cls._instances[feature_name]

    def __init__(self, entry: str) -> None:
        if not hasattr(self, "name"):
            self.name: str = FeatureUtils.feature_name_from(entry)
            self.root_params: root_FeatureParams_dict | None = None
            self.required_features: list[str] = []
            self.shared_content = FeatureSharedContent()
            self.lifespan = FeatureLifespan()

            self.frames: AbsFrames = None
            self.params: AbsParams = None
            self.logger: AbsLogger = None

    def dialog(
        self,
        message: str,
        level: Literal["INFO", "WARNING"] = "INFO",
        title: str = "Vixen Shell",
    ) -> None: ...

    def init(self, value: root_FeatureParams_dict):
        self.root_params = value

    def set_required_features(self, value: list[str]):
        self.required_features = value

    def share(self, content_type: FeatureContentType):
        def decorator(callback: Callable):
            try:
                sub_contents: dict[str, Callable] = getattr(
                    self.shared_content, content_type
                )

            except AttributeError:
                raise ValueError(
                    f"Invalid content type: '{content_type}', "
                    f"in file: {callback.__code__.co_filename}, "
                    f"at line: {callback.__code__.co_firstlineno}"
                )

            if sub_contents.get(callback.__name__):
                raise Exception(
                    f"{content_type.capitalize()} content '{callback.__name__}' already shared"
                )

            sub_contents[callback.__name__] = callback
            return callback

        return decorator

    def on_startup(self, callback: Callable[[], None]):
        if self.lifespan.startup_callback:
            raise Exception(
                "Startup sequence already defined "
                f"in file: {callback.__code__.co_filename}, "
                f"at line: {callback.__code__.co_firstlineno}"
            )

        self.lifespan.startup_callback = callback
        return callback

    def on_shutdown(self, callback: Callable[[], None]):
        if self.lifespan.shutdown_callback:
            raise Exception(
                "Shutdown sequence already defined "
                f"in file: {callback.__code__.co_filename}, "
                f"at line: {callback.__code__.co_firstlineno}"
            )

        self.lifespan.shutdown_callback = callback
        return callback
