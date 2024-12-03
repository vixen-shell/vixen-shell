import os, sys, logging
from multiprocessing import Process
from vx_config import VxConfig
from vx_cli import Cli
from .FlaskApp import FlaskApp
from ..front_app import app
from ..utils import front_logging_config


def get_current_tty():
    try:
        return os.ttyname(sys.stdout.fileno())
    except:
        return None


class Formatter(logging.Formatter):
    def format(self, record):
        message = record.getMessage()

        levelname = Cli.String.level(record.levelname, record.levelname)
        levelname += ":" + Cli.String.spaces(9 - len(record.levelname))
        message = f"[Front server]: {message}"

        return levelname + message


def server_process():
    tty_path = get_current_tty()

    if tty_path:
        file_handler = logging.FileHandler(tty_path)
        file_handler.setFormatter(Formatter())

        logger = logging.getLogger("gunicorn")
        logger.addHandler(file_handler)

    FlaskApp(
        app,
        {
            "bind": f"localhost:{VxConfig.FRONT_PORT}",
            "logconfig_dict": front_logging_config,
        },
    ).run()


class FrontServer:
    process: Process = None

    @staticmethod
    def start():
        if FrontServer.process:
            raise ValueError(f"{FrontServer.__name__} already running")

        FrontServer.process = Process(target=server_process)
        FrontServer.process.start()

    @staticmethod
    def stop():
        if not FrontServer.process:
            raise ValueError(f"{FrontServer.__name__} is not running")

        FrontServer.process.terminate()
