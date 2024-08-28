import subprocess, threading
from typing import TypedDict
from vx_root import content


class ProcessInfos(TypedDict):
    pid: int
    command: str
    args: list[str]


@content().dispatch("task")
def run(command: str, args: list[str] = [], wait_process: bool = False) -> ProcessInfos:
    process = subprocess.Popen(
        [command] + args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    if wait_process:
        threading.Thread(target=process.wait).start()

    return ProcessInfos(pid=process.pid, command=command, args=args)
