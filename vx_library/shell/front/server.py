import logging, multiprocessing
from flask import Flask, send_from_directory
from gunicorn.app.base import BaseApplication
from ..logger import Logger


class FlaskApp(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key, value)

    def load(self):
        return self.application


app = Flask(__name__)


@app.route("/")
def index():
    return send_from_directory("/var/opt/vx-front-main/dist", "index.html")


@app.route("/<path:name>")
def path_name(name: str):
    return send_from_directory("/var/opt/vx-front-main/dist", name)


logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {
        "level": "INFO",
        "propagate": True,
    },
    "loggers": {
        "gunicorn.error": {
            "level": "INFO",
            "propagate": True,
            "qualname": "gunicorn.error",
        },
        "gunicorn.access": {
            "level": "ERROR",
            "propagate": True,
            "qualname": "gunicorn.access",
        },
    },
    "formatters": {
        "generic": {
            "format": "%(levelname)s: (Front server) %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter",
        }
    },
}


def run_server():
    class LogHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            Logger.log(f"Front-end: {record.getMessage()}", record.levelname)

    logger = logging.getLogger("gunicorn")
    logger.addHandler(LogHandler())

    FlaskApp(app, {"bind": "localhost:6492", "logconfig_dict": logging_config}).run()


server_process = multiprocessing.Process(target=run_server)


class FrontServer:
    @staticmethod
    def run():
        server_process.start()

    @staticmethod
    def stop():
        server_process.terminate()
