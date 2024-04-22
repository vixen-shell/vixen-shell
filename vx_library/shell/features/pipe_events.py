from typing import TypedDict, Optional, Literal
from ..log import LogLevel, LogData


class EventData:
    class StateItem(TypedDict):
        key: str
        value: None | str | int | float | bool

    class Log(TypedDict):
        level: LogLevel
        purpose: str
        data: Optional[LogData]


class InputEvent(TypedDict):
    id: Literal["GET_STATE", "SET_STATE", "SAVE_STATE", "LOG"]
    data: Optional[EventData.StateItem | EventData.Log]


class OutputEvent(TypedDict):
    id: Literal["UPDATE_STATE", "LOG"]
    data: Optional[EventData.StateItem | EventData.Log]
