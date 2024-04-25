import multiprocessing, logging
from .FlaskApp import FlaskApp
from ..front_app import app
from ..utils import front_logging_config
from ...globals import FRONT_PORT
from ...logger import Logger


def server_process():
    class LogHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            Logger.log(f"[Front server]: {record.getMessage()}", record.levelname)

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
    process: multiprocessing.Process = None

    @staticmethod
    def run():
        if FrontServer.process:
            raise ValueError(f"{FrontServer.__name__} already running")

        FrontServer.process = multiprocessing.Process(target=server_process)
        FrontServer.process.start()

    @staticmethod
    def stop():
        if not FrontServer.process:
            raise ValueError(f"{FrontServer.__name__} is not running")

        FrontServer.process.terminate()
