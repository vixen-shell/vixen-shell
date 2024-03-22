from flask import Flask, send_from_directory
from gunicorn.app.base import BaseApplication


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


def run_front_server():
    FlaskApp(app, {"bind": "localhost:6492"}).run()
