from flask import Flask, send_from_directory
from vx_path import VxPath

app = Flask(__name__)


@app.route("/")
def index():
    return send_from_directory(VxPath.FRONT_DIST, "index.html")


@app.route("/<path:name>")
def path_name(name: str):
    return send_from_directory(VxPath.FRONT_DIST, name)
