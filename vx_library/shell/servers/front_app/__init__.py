from flask import Flask, send_from_directory
from ...globals import FRONT_DIST_DIRECTORY

app = Flask(__name__)


@app.route("/")
def index():
    return send_from_directory(FRONT_DIST_DIRECTORY, "index.html")


@app.route("/<path:name>")
def path_name(name: str):
    return send_from_directory(FRONT_DIST_DIRECTORY, name)
