from fastapi.middleware.cors import CORSMiddleware
from vx_config import VxConfig
from .api import api


api.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://localhost:{VxConfig.FRONT_PORT}",
        f"http://localhost:{VxConfig.FRONT_DEV_PORT}",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
