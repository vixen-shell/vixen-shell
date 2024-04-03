import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from .log import Logger
from .globals import API_PORT, FRONT_PORT, FRONT_DEV_PORT
from .features import Features
from .front import FrontServer

api_server: uvicorn.Server = None


@asynccontextmanager
async def lifespan(api: FastAPI):
    Features.startup()
    yield
    await Features.cleanup()
    FrontServer.stop()


api = FastAPI(lifespan=lifespan)


@api.get("/ping", description="Test API availability")
async def ping():
    return "Vixen Shell API (1.0.0)"


@api.get("/shutdown", description="Close API")
async def close():
    api_server.should_exit = True
    return


# ENDPOINTS
from . import log_endpoints
from . import features_endpoints
from . import frames_endpoints

# WEBSOCKETS
from . import features_websockets
from . import hypr_websockets


def run_api():
    global api_server
    api_server = uvicorn.Server(uvicorn.Config(api, host="localhost", port=API_PORT))

    api.add_middleware(
        CORSMiddleware,
        allow_origins=[
            f"http://localhost:{FRONT_PORT}",
            f"http://localhost:{FRONT_DEV_PORT}",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if Features.init():
        Logger.init()
        FrontServer.run()
        api_server.run()


# from . import static_endpoints
