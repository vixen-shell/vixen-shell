from pydantic import BaseModel
from typing import Dict, List, Literal


# COMMONS MODELS
class Commons_Error(BaseModel):
    message: str
    shell_error: bool = True


# LOG MODELS
class Log_Log(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    message: str


class Log_Logs(BaseModel):
    logs: List[Log_Log]


# FEATURES MODELS
class Features_Names(BaseModel):
    names: List[str]


class Features_Base(BaseModel):
    name: str
    is_started: bool = True


class Features_State(Features_Base):
    state: Dict[str, None | str | int | float | bool]


class Features_LogListener(Features_Base):
    log_listener: bool


# FRAMES MODELS
class Frames_Ids(BaseModel):
    ids: List[str]
    actives: List[str]


class Frames_Base(BaseModel):
    id: str
    is_opened: bool = True


class Frames_Properties(Frames_Base):
    feature: Features_Base


# OS MODELS
class Os_ExecInfo(BaseModel):
    pid: int
    command: str
    args: list[str]
