import uvicorn
from fastapi import FastAPI
from .globals import API_PORT
from .log import Logger
from .hypr_events import HyprEventsListener
from .features import Features
from .front import FrontServer


class ApiServer:
    server: uvicorn.Server = None

    @staticmethod
    def init_server(api: FastAPI):
        ApiServer.server = uvicorn.Server(
            uvicorn.Config(api, host="localhost", port=API_PORT)
        )

        Logger.init()

    @staticmethod
    def init_requirements():
        if not ApiServer.server:
            return False

        if not HyprEventsListener.check_hypr_socket():
            Logger.log("WARNING", "Hyprland socket not found")
            Logger.log("INFO", "Sorry, Vixen Shell only starts with Hyprland")
            return False
        else:
            Logger.log("INFO", "Hyprland socket found")

        if not Features.init():
            Logger.log("WARNING", "Sorry, unable to initialize features")
            return False
        else:
            Logger.log("INFO", "Features initialization successful")

        return True

    @staticmethod
    def run(api: FastAPI):
        ApiServer.init_server(api)

        if ApiServer.init_requirements():
            FrontServer.run()
            ApiServer.server.run()
