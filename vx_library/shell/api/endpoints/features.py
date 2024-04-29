import time
from fastapi import Response, Path, Body
from ..api import api
from ...globals import ModelResponses, Models
from ...features import Features
from ...servers import FrontServer

# FEATURE NAMES
names_responses = ModelResponses({200: Models.Features.Names})


@api.get(
    "/features/names",
    description="Get available feature names",
    responses=names_responses.responses,
)
async def feature_names(response: Response):
    return names_responses(response, 200)(names=Features.names())


# RELOAD FEATURES
reload_responses = ModelResponses(
    {200: Models.Features.Names, 409: Models.Commons.Error}
)


@api.get(
    "/features/reload",
    description="Reload features",
    responses=names_responses.responses,
)
async def feature_names(response: Response):
    await Features.stop()
    FrontServer.restart()

    time.sleep(5)

    if not Features.init():
        return reload_responses(response, 409)(message="Unable to reload features")

    Features.startup()
    return names_responses(response, 200)(names=Features.names())
