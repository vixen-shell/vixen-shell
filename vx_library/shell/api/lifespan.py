from fastapi import FastAPI
from contextlib import asynccontextmanager
from ..features import Features
from ..servers import FrontServer
from ..hypr_events import HyprEventsListener


@asynccontextmanager
async def lifespan(api: FastAPI):
    HyprEventsListener.start()
    Features.init()
    yield
    await Features.stop()
    HyprEventsListener.stop()
    FrontServer.stop()
