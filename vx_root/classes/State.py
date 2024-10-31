from typing import Callable, TypedDict, Any


class StateItem(TypedDict):
    key: str
    value: Any


class State:
    @staticmethod
    def add_listener(listener: Callable[[StateItem], None]) -> None:
        from vx_config import VxConfig

        return VxConfig.add_state_listener(listener)

    @staticmethod
    def remove_listener(listener: Callable[[StateItem], None]) -> None:
        from vx_config import VxConfig

        return VxConfig.remove_state_listener(listener)

    @staticmethod
    def get(key: str) -> Any:
        from vx_config import VxConfig

        return VxConfig.get_state(key)

    @staticmethod
    def set(key: str, value: Any) -> None:
        from vx_config import VxConfig

        return VxConfig.set_state(key, value)
