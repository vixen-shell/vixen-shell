import subprocess, threading
from . import content


@content.add_handler("action")
def run(command: str, args: list[str] = [], wait_process: bool = False):
    process = subprocess.Popen(
        [command] + args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    if wait_process:
        threading.Thread(target=process.wait).start()

    return {"pid": process.pid, "command": command, "args": args}
