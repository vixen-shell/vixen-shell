from typing import Literal, Callable, Any
from .SocketHandler import SocketHandler
from .AbstractFeature import AbstractFeature
from ..params import root_FeatureParams_dict
from ..utils import feature_name_from

FeatureContentType = Literal["action", "data", "file", "socket"]


class FeatureSharedContent:
    def __init__(self):
        self.action: dict[str, Callable[[], None]] = {}
        self.data: dict[str, Callable[[], Any]] = {}
        self.file: dict[str, Callable[[], str]] = {}
        self.socket: dict[str, Callable[[], SocketHandler]] = {}


class FeatureLifespan:
    def __init__(self):
        self.__startup_callback: Callable[[], None] | None = None
        self.__shutdown_callback: Callable[[], None] | None = None

    def startup(self):
        if self.__startup_callback:
            self.__startup_callback()

    def shutdown(self):
        if self.__shutdown_callback:
            self.__shutdown_callback()


class RootFeature:
    _instances = {}

    @classmethod
    def del_instance(cls, entry: str):
        feature_name = feature_name_from(entry)

        if feature_name in cls._instances:
            del cls._instances[feature_name]

    def __new__(cls, entry: str):
        feature_name = feature_name_from(entry)

        if feature_name not in cls._instances:
            cls._instances[feature_name] = super().__new__(cls)

        return cls._instances[feature_name]

    def __init__(self, entry: str) -> None:
        if not hasattr(self, "_RootFeature__feature_name"):
            self.__feature_name: str = entry
            self.__root_params: root_FeatureParams_dict | None = None
            self.__required_features: list[str] = []
            self.__shared_content = FeatureSharedContent()
            self.__lifespan = FeatureLifespan()

            self.current: AbstractFeature = None

    def init(self, value: root_FeatureParams_dict):
        self.__root_params = value

    def set_required_features(self, value: list[str]):
        self.__required_features = value

    def share(self, content_type: FeatureContentType):
        def decorator(callback: Callable):
            try:
                sub_contents: dict[str, Callable] = getattr(
                    self.__shared_content, content_type
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
        if self.__lifespan.__startup_callback:
            raise Exception(
                "Startup sequence already defined "
                f"in file: {callback.__code__.co_filename}, "
                f"at line: {callback.__code__.co_firstlineno}"
            )

        self.__lifespan.__startup_callback = callback
        return callback

    def on_shutdown(self, callback: Callable[[], None]):
        if self.__lifespan.__shutdown_callback:
            raise Exception(
                "Shutdown sequence already defined "
                f"in file: {callback.__code__.co_filename}, "
                f"at line: {callback.__code__.co_firstlineno}"
            )

        self.__lifespan.__shutdown_callback = callback
        return callback
