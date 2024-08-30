from typing import Literal
from .references import AbsLogger, get_logger_reference


class RootUtils:
    from .classes import SocketHandler

    @property
    def logger(self) -> AbsLogger: ...

    def dialog(
        self,
        message: str,
        level: Literal["INFO", "WARNING"] = "INFO",
        title: str = "Vixen Shell",
    ) -> None: ...


def get_utils() -> RootUtils:
    from vx_shell.logger import Logger
    from vx_shell.features.Gtk_dialog import show_dialog_box

    root_utils = RootUtils()
    root_utils.logger = get_logger_reference(Logger)
    root_utils.dialog = show_dialog_box

    return RootUtils


utils = get_utils()
