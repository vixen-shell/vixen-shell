from threading import Thread
from multiprocessing import Process, Queue
from queue import Empty as QueueEmpty
from .FlaskApp import FlaskApp
from ..front_app import app
from ..utils import init_front_logging, front_logging_config
from ...globals import FRONT_PORT
from ...logger import Logger


def server_process(queue: Queue):
    init_front_logging(queue)

    FlaskApp(
        app,
        {
            "bind": f"localhost:{FRONT_PORT}",
            "logconfig_dict": front_logging_config,
        },
    ).run()


class FrontServer:
    process: Process = None
    queue: Queue = Queue()

    @staticmethod
    def handle_queue():
        Logger.log(f"[Front server]: Start listening logs", "INFO")

        while FrontServer.process.is_alive():
            try:
                log = FrontServer.queue.get(timeout=1)
                Logger.log(f"[Front server]: {log['message']}", log["level"])

                if log["message"] == "Shutting down: Master":
                    break

            except QueueEmpty:
                continue

        Logger.log(f"[Front server]: Stop listening logs", "INFO")

    @staticmethod
    def run():
        if FrontServer.process:
            raise ValueError(f"{FrontServer.__name__} already running")

        FrontServer.process = Process(target=server_process, args=(FrontServer.queue,))
        FrontServer.process.start()
        Thread(target=FrontServer.handle_queue).start()

    @staticmethod
    def stop():
        if not FrontServer.process:
            raise ValueError(f"{FrontServer.__name__} is not running")

        FrontServer.process.terminate()
