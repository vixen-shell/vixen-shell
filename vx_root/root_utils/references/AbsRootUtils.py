from typing import Literal
from abc import ABC, abstractmethod
from .AbsLogger import AbsLogger, get_logger_reference


class AbsRootUtils(ABC):
    @property
    @abstractmethod
    def logger(self) -> AbsLogger: ...

    @abstractmethod
    def dialog(
        self,
        message: str,
        level: Literal["INFO", "WARNING"] = "INFO",
        title: str = "Vixen Shell",
    ) -> None: ...


def get_root_utils_reference():
    from vx_logger import Logger
    from vx_gtk import show_dialog_box

    Logger_reference = get_logger_reference(Logger)

    class RootUtilsReference(AbsRootUtils):
        from ..classes import ContextMenu, SocketHandler

        @property
        def logger(self) -> AbsLogger:
            return Logger_reference

        def dialog(
            self,
            message: str,
            level: Literal["INFO", "WARNING"] = "INFO",
            title: str = "Vixen Shell",
        ) -> None:
            return show_dialog_box(message, level, title)

    return RootUtilsReference()
