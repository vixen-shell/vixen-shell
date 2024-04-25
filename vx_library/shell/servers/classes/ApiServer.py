import uvicorn
from fastapi import FastAPI
from .FrontServer import FrontServer
from ..utils import api_logging_config, init_api_requirements
from ...globals import API_PORT
from ...logger import Logger


class ApiServer:
    server: uvicorn.Server = None

    @staticmethod
    def run(api: FastAPI):
        if ApiServer.server:
            raise ValueError(f"{ApiServer.__name__} already running")

        ApiServer.server = uvicorn.Server(
            uvicorn.Config(
                api, host="localhost", port=API_PORT, log_config=api_logging_config
            )
        )

        Logger.init()

        if init_api_requirements():
            FrontServer.run()
            ApiServer.server.run()
