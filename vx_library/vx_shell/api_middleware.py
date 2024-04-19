from .api import api
from fastapi.middleware.cors import CORSMiddleware
from .globals import FRONT_PORT, FRONT_DEV_PORT

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
