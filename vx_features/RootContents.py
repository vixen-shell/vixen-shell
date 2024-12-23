from typing import Callable
from vx_types import FeatureContentType
from .utils import FeatureUtils


class rootcontent: ...


class RootContents:
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
            self.name = FeatureUtils.feature_name_from(entry)
            self.task = rootcontent()
            self.data = rootcontent()
            self.socket = rootcontent()
            self.menu = rootcontent()

    def dispatch(self, content_type: FeatureContentType, name: str = None):
        def decorator(callback: Callable):
            content_name = callback.__name__ if name is None else name

            try:
                sub_content: rootcontent = getattr(self, content_type)
            except AttributeError:
                raise ValueError(
                    f"Invalid content type: '{content_type}', "
                    f"in file: {callback.__code__.co_filename}, "
                    f"at line: {callback.__code__.co_firstlineno}"
                )

            if content_name in sub_content.__dict__:
                raise Exception(
                    f"{content_type.capitalize()} content "
                    f"'{content_name}' already dispatched"
                )

            sub_content.__dict__[content_name] = callback
            return callback

        return decorator

    def undispatch(self, content_type: FeatureContentType, name: str):
        try:
            sub_content: rootcontent = getattr(self, content_type)
        except AttributeError:
            raise ValueError(f"Invalid content type: '{content_type}'")

        if not name in sub_content.__dict__:
            raise Exception(
                f"{content_type.capitalize()} content " f"'{name}' is not dispatched"
            )

        sub_content.__dict__.pop(name)

    def exists(self, content_type: FeatureContentType, name: str) -> bool:
        try:
            sub_content: rootcontent = getattr(self, content_type)
        except AttributeError:
            raise ValueError(f"Invalid content type: '{content_type}'")

        return name in sub_content.__dict__

    def get(self, content_type: FeatureContentType, name: str) -> Callable:
        sub_content: rootcontent = getattr(self, content_type)
        return sub_content.__dict__[name]
