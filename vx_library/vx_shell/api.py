from fastapi import FastAPI
from .api_lifespan import lifespan


api = FastAPI(lifespan=lifespan)

from . import api_middleware
from .endpoints import *
from .websocket import *
