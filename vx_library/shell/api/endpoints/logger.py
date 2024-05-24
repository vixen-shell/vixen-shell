from fastapi import Response, Body
from typing import Optional
from ..api import api
from ...globals import ModelResponses, Models
from ...logger import Log, LogLevel, Logger

log_cache_size = 512
log_cache: list[Log] = []


def handle_log_cache(log: Log):
    if len(log_cache) == log_cache_size:
        log_cache.pop(0)

    log_cache.append(log)


Logger.add_listener(handle_log_cache)

# ---------------------------------------------- - - -
# GET LOGS
#

logs_responses = ModelResponses({200: Models.Log.Logs})


@api.get("/logs", description="Get logs", responses=logs_responses.responses)
async def get_logs(response: Response):
    return logs_responses(response, 200)(logs=log_cache)


# ---------------------------------------------- - - -
# POST LOG
#

log_responses = ModelResponses({200: Models.Log.Log})


@api.post("/log", description="Post a log", responses=log_responses.responses)
async def post_log(
    response: Response,
    level: Optional[LogLevel] = Body(description="Level", default="INFO"),
    message: str = Body(description="Message"),
):
    Logger.log(message, level)

    return log_responses(response, 200)(level=level, message=message)
