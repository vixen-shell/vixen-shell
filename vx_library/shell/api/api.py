from fastapi import FastAPI
from .lifespan import lifespan


api = FastAPI(lifespan=lifespan)

from . import middlewares
from .endpoints import *
from .websocket import *
