from fastapi import Response, Body
from typing import Literal, Optional, Dict
from .api import api
from .globals import ModelResponses, Models
from .log import Logger

# GET LOGS
logs_responses = ModelResponses({200: Models.Log.Logs})


@api.get("/logs", description="Get logs", responses=logs_responses.responses)
async def get_logs(response: Response):
    return logs_responses(response, 200)(logs=Logger.log_cache)


log_responses = ModelResponses({200: Models.Log.Log})


@api.post("/log", description="Post a log", responses=log_responses.responses)
async def post_log(
    response: Response,
    level: Optional[Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]] = Body(
        description="Level log", default="INFO"
    ),
    purpose: str = Body(description="Purpose log"),
    data: Optional[Models.Log.LogData] = Body(
        description="Optional data", default=None
    ),
):
    Logger.log(level, purpose, data)

    return log_responses(response, 200)(level=level, purpose=purpose, data=data)
