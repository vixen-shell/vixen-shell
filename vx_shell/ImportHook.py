import builtins
from typing import Mapping, Sequence
from types import ModuleType
from pathlib import Path


class ImportHook:
    env_path = Path(__file__).parents[1].as_posix()
    original_import = builtins.__import__
    protected_packages = ["vx_cli", "vx_features", "vx_manager", "vx_shell", "vx_types"]

    @staticmethod
    def custom_import(
        name: str,
        globals: Mapping[str, object] | None = None,
        locals: Mapping[str, object] | None = None,
        fromlist: Sequence[str] = (),
        level: int = 0,
    ) -> ModuleType:
        if name.startswith(tuple(ImportHook.protected_packages)) and not globals[
            "__file__"
        ].startswith(ImportHook.env_path):
            raise PermissionError(f"Unable to import {name} from {globals['__file__']}")

        return ImportHook.original_import(name, globals, locals, fromlist, level)

    @staticmethod
    def init():
        builtins.__import__ = ImportHook.custom_import
