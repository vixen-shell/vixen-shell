import uvicorn
from fastapi import FastAPI
from vx_config import VxConfig
from vx_logger import Logger
from .FrontServer import FrontServer
from ..utils import api_logging_config


class ApiServer:
    server: uvicorn.Server = None

    @staticmethod
    def start(api: FastAPI):
        if ApiServer.server:
            raise ValueError(f"{ApiServer.__name__} already running")

        ApiServer.server = uvicorn.Server(
            uvicorn.Config(
                api,
                host="localhost",
                port=VxConfig.API_PORT,
                log_config=api_logging_config,
            )
        )

        Logger.init()
        FrontServer.start()

        try:
            ApiServer.server.run()
        except KeyboardInterrupt:
            ApiServer.server.should_exit = True
