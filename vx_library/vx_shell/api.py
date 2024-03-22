import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from .log import Logger
from .globals import DevMode, get_front_url
from .features import Features

origins = ["http://localhost:5173", "http://localhost:6492"]


@asynccontextmanager
async def lifespan(api: FastAPI):
    Features.startup()
    yield
    await Features.cleanup()


api = FastAPI(lifespan=lifespan)

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = uvicorn.Config(api, host="localhost", port=6481)
server = uvicorn.Server(config)


@api.get("/ping", description="Test API availability")
async def ping():
    return "Vixen Shell API (1.0.0)"


@api.get("/shutdown", description="Close API")
async def close():
    server.should_exit = True
    return


# ENDPOINTS
from . import log_endpoints
from . import features_endpoints
from . import frames_endpoints

# WEBSOCKETS
from . import features_websockets
from . import hypr_websockets

# LOGGER
Logger.init()


def run(dev_mode: bool = False):
    if dev_mode:
        DevMode.set(True)
        Logger.log("INFO", f"Front URL: {get_front_url()} (dev mode)")
    if Features.init():
        server.run()


# from . import static_endpoints
