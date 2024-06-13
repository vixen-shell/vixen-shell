from fastapi import FastAPI
from contextlib import asynccontextmanager
from ..features import Features
from ..servers import FrontServer


@asynccontextmanager
async def lifespan(api: FastAPI):
    Features.init()
    yield
    await Features.stop()
    FrontServer.stop()
