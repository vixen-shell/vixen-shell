import uvicorn
from fastapi import FastAPI
from .FrontServer import FrontServer
from ..utils import api_logging_config
from ...globals import API_PORT
from ...logger import Logger
from ...hypr_events import HyprEventsListener


class ApiServer:
    server: uvicorn.Server = None

    @staticmethod
    def start(api: FastAPI):
        if ApiServer.server:
            raise ValueError(f"{ApiServer.__name__} already running")

        ApiServer.server = uvicorn.Server(
            uvicorn.Config(
                api, host="localhost", port=API_PORT, log_config=api_logging_config
            )
        )

        Logger.init()

        if not HyprEventsListener.check_hypr_socket():
            Logger.log("Hyprland socket not found", "WARNING")
            Logger.log("Sorry, Vixen Shell only starts with Hyprland")
            return

        Logger.log("Hyprland socket found")

        FrontServer.start()
        ApiServer.server.run()
