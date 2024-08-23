from abc import ABC, abstractmethod
from typing import Callable, Any


class AbsParams(ABC):
    @abstractmethod
    def add_param_listener(
        self, param_path: str, listener: Callable[[str, Any], None]
    ) -> None:
        pass

    @abstractmethod
    def remove_param_listener(
        self, param_path: str, listener: Callable[[str, Any], None]
    ) -> None:
        pass

    @abstractmethod
    def node_is_define(self, node_path: str) -> bool:
        pass

    @property
    @abstractmethod
    def state_is_enable(self) -> bool:
        pass

    @property
    @abstractmethod
    def state(self) -> dict:
        pass

    @abstractmethod
    def save_params(self) -> None:
        pass

    @abstractmethod
    def get_value(self, param_path: str) -> Any | None:
        pass

    @abstractmethod
    def set_value(self, param_path: str, value: Any) -> None:
        pass


def get_params_reference(feature_name: str, ParamDataHandler):
    class ParamHandlerReference(AbsParams):
        def add_param_listener(
            self, param_path: str, listener: Callable[[str, Any], None]
        ) -> None:
            path = f"{feature_name}.{param_path}"
            ParamDataHandler.add_param_listener(path, listener)

        def remove_param_listener(
            self, param_path: str, listener: Callable[[str, Any], None]
        ) -> None:
            path = f"{feature_name}.{param_path}"
            ParamDataHandler.remove_param_listener(path, listener)

        def node_is_define(self, node_path: str) -> bool:
            path = f"{feature_name}.{node_path}"
            return ParamDataHandler.node_is_define(path)

        @property
        def state_is_enable(self) -> bool:
            return ParamDataHandler.state_is_enable(feature_name)

        @property
        def state(self) -> dict:
            return ParamDataHandler.get_state(feature_name)

        def save_params(self) -> None:
            ParamDataHandler.save_params(feature_name)

        def get_value(self, param_path: str) -> Any | None:
            path = f"{feature_name}.{param_path}"
            return ParamDataHandler.get_value(path)

        def set_value(self, param_path: str, value: Any) -> None:
            path = f"{feature_name}.{param_path}"
            ParamDataHandler.set_value(path, value)

    return ParamHandlerReference()
