from typing import TypedDict, Optional, Literal
from ..logger import LogLevel


class EventData:
    class StateItem(TypedDict):
        key: str
        value: None | str | int | float | bool

    class Log(TypedDict):
        level: LogLevel
        message: str


class InputEvent(TypedDict):
    id: Literal["GET_STATE", "SET_STATE", "SAVE_STATE", "LOG"]
    data: Optional[EventData.StateItem | EventData.Log]


class OutputEvent(TypedDict):
    id: Literal["UPDATE_STATE", "LOG"]
    data: Optional[EventData.StateItem | EventData.Log]
