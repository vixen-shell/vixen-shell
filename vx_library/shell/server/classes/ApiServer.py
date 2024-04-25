import uvicorn
from fastapi import FastAPI
from ..utils import logging_config, init_requirements
from ...globals import API_PORT
from ...logger import Logger
from ...front import FrontServer


class ApiServer:
    server: uvicorn.Server = None

    @staticmethod
    def run(api: FastAPI):
        if ApiServer.server:
            raise ValueError(f"{ApiServer.__name__} already initialized")

        ApiServer.server = uvicorn.Server(
            uvicorn.Config(
                api, host="localhost", port=API_PORT, log_config=logging_config
            )
        )

        Logger.init()

        if init_requirements():
            FrontServer.run()
            ApiServer.server.run()
