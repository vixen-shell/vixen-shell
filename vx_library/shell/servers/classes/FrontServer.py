import logging
from threading import Thread
from multiprocessing import Process, Queue
from queue import Empty as QueueEmpty
from .FlaskApp import FlaskApp
from ..front_app import app
from ..utils import front_logging_config
from ...globals import FRONT_PORT
from ...logger import Logger


def server_process(queue: Queue):
    class LogHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            queue.put({"level": record.levelname, "message": record.getMessage()})

    logger = logging.getLogger("gunicorn")
    logger.addHandler(LogHandler())

    FlaskApp(
        app,
        {
            "bind": f"localhost:{FRONT_PORT}",
            "logconfig_dict": front_logging_config,
        },
    ).run()


class FrontServer:
    process: Process = None
    log_handler: Thread = None

    @staticmethod
    def init_log_handler():
        queue = Queue()

        def handle_log():
            Logger.log(f"[Front server]: Start listening logs", "INFO")

            while FrontServer.process.is_alive():
                try:
                    log = queue.get(timeout=1)
                    Logger.log(f"[Front server]: {log['message']}", log["level"])

                    if log["message"] == "Shutting down: Master":
                        break

                except QueueEmpty:
                    continue

            Logger.log(f"[Front server]: Stop listening logs", "INFO")

        thread = Thread(target=handle_log)

        return thread, queue

    @staticmethod
    def start():
        if FrontServer.process:
            raise ValueError(f"{FrontServer.__name__} already running")

        FrontServer.log_handler, queue = FrontServer.init_log_handler()
        FrontServer.process = Process(target=server_process, args=(queue,))

        FrontServer.process.start()
        FrontServer.log_handler.start()

    @staticmethod
    def stop():
        if not FrontServer.process:
            raise ValueError(f"{FrontServer.__name__} is not running")

        FrontServer.process.terminate()
        FrontServer.log_handler.join()

        FrontServer.process = None
        FrontServer.log_handler = None

    def restart():
        FrontServer.stop()
        FrontServer.start()
