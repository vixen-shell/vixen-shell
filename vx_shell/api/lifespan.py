from fastapi import FastAPI
from contextlib import asynccontextmanager
from vx_systray import SysTrayObserver
from ..features import Features
from ..servers import FrontServer


@asynccontextmanager
async def lifespan(api: FastAPI):
    FrontServer.start()
    SysTrayObserver.start()
    Features.init()
    yield
    await Features.stop()
    SysTrayObserver.stop()
    FrontServer.stop()
