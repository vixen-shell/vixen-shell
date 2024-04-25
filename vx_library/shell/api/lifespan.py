from fastapi import FastAPI
from contextlib import asynccontextmanager
from ..features import Features
from ..servers import FrontServer
from ..hypr_events import HyprEventsListener


@asynccontextmanager
async def lifespan(api: FastAPI):
    HyprEventsListener.start()
    Features.startup()
    yield
    await Features.cleanup()
    HyprEventsListener.stop()
    FrontServer.stop()
