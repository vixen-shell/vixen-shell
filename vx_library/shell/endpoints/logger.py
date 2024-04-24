from fastapi import Response, Body
from typing import Literal, Optional
from ..api import api
from ..globals import ModelResponses, Models
from ..logger import Logger, LogLevel

# GET LOGS
logs_responses = ModelResponses({200: Models.Log.Logs})


@api.get("/logs", description="Get logs", responses=logs_responses.responses)
async def get_logs(response: Response):
    return logs_responses(response, 200)(logs=Logger.log_cache)


log_responses = ModelResponses({200: Models.Log.Log})


@api.post("/log", description="Post a log", responses=log_responses.responses)
async def post_log(
    response: Response,
    level: Optional[LogLevel] = Body(description="Level log", default="INFO"),
    message: str = Body(description="Purpose log"),
):
    Logger.log(level, message)

    return log_responses(response, 200)(level=level, message=message)
