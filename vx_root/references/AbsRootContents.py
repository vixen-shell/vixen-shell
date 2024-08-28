from inspect import stack, getmodule
from abc import ABC, abstractmethod
from typing import Callable
from vx_types import FeatureContentType


class AbsRootContents(ABC):
    @property
    @abstractmethod
    def task(self) -> object:
        pass

    @property
    @abstractmethod
    def data(self) -> object:
        pass

    @property
    @abstractmethod
    def file(self) -> object:
        pass

    @abstractmethod
    def dispatch(
        self, content_type: FeatureContentType, name: str = None
    ) -> Callable[[Callable], Callable]:
        pass

    @abstractmethod
    def get(self, content_type: FeatureContentType, name: str) -> Callable:
        pass


def get_root_contents_reference(root_contents):
    def restricted(contents_name: str = None):
        def decorator(attribute):
            def wrapper(*args, **kwargs):
                package_name = getmodule(stack()[1].frame).__package__

                if not package_name:
                    raise PermissionError(
                        f"The usage of the '{attribute.__name__}' attribute only "
                        "applies in the context of a feature package"
                    )

                if contents_name:
                    if not package_name.split(".")[0] == contents_name:
                        raise PermissionError(
                            f"The usage of the '{attribute.__name__}' attribute is only "
                            "applicable in the context of the original feature package"
                        )

                return attribute(*args, **kwargs)

            return wrapper

        return decorator

    class RootContentsReference(AbsRootContents):
        @property
        @restricted()
        def task(self) -> object:
            return root_contents.task

        @property
        @restricted()
        def data(self) -> object:
            return root_contents.data

        @property
        @restricted()
        def file(self) -> object:
            return root_contents.file

        @restricted(root_contents.name)
        def dispatch(
            self, content_type: FeatureContentType, name: str = None
        ) -> Callable[[Callable], Callable]:
            return root_contents.dispatch(content_type, name)

        @restricted(root_contents.name)
        def get(self, content_type: FeatureContentType, name: str) -> Callable:
            return root_contents.get(content_type, name)

    return RootContentsReference()
