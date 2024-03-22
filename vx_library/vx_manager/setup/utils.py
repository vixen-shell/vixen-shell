import subprocess
from typing import TypedDict


class Outputs(TypedDict):
    out: bool
    err: bool


def exec(command: str, outputs: Outputs = {"out": False, "err": True}) -> bool:
    if (
        subprocess.run(
            command,
            stdout=subprocess.PIPE if not outputs["out"] else None,
            stderr=subprocess.PIPE if not outputs["err"] else None,
            shell=True,
        ).returncode
        == 0
    ):
        return True
    return False
