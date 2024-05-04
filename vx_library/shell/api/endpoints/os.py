import subprocess, threading, time
from fastapi import Response, Body
from ..api import api
from ...globals import ModelResponses, Models

# ---------------------------------------------- - - -
# OS EXEC
#

exec_responses = ModelResponses(
    {
        200: Models.Os.ExecInfo,
        404: Models.Commons.Error,
    }
)

process_outputs = {}
active_processes = {}


class PopenProcess:
    def __init__(self, command: str, args: list[str] = [], keep_output: bool = False):
        self.command = command
        self.args = args
        self.keep_output = keep_output
        self.is_alive = False

    def run(self):
        if not self.is_alive:
            self.process = subprocess.Popen(
                [self.command] + self.args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self.id = str(self.process.pid) + str(time.time()).replace(".", "")
            active_processes[self.id] = self

            threading.Thread(target=self.process_wait).start()

            return {
                "id": self.id,
                "pid": self.process.pid,
                "command": self.command,
                "args": self.args,
            }

    def process_wait(self):
        self.process.wait()
        self.is_alive = False
        del active_processes[self.id]

        if self.keep_output:
            stdout, stderr = self.process.communicate()

            process_outputs[self.id] = {
                "command": self.command,
                "args": self.args,
                "exitcode": self.process.returncode,
                "stdout": stdout,
                "stderr": stderr,
            }


@api.post(
    "/os/run", description="Run linux command", responses=exec_responses.responses
)
async def post_log(
    response: Response,
    command: str = Body(description="Command"),
    args: list[str] = Body(description="Optional command arguments", default=[]),
    keep_output: bool = Body(description="Keep output command", default=False),
):
    process = PopenProcess(command, args, keep_output)

    try:
        exec_info = process.run()
        return exec_responses(response, 200)(**exec_info)

    except Exception as exception:
        return exec_responses(response, 404)(message=str(exception))
