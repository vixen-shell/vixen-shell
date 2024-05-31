from fastapi import Response, Body
from ..api import api
from ...globals import ModelResponses, Models
from ...features import Features

# ---------------------------------------------- - - -
# FEATURE NAMES
#

names_responses = ModelResponses({200: Models.Features.Names})


@api.get(
    "/features/names",
    description="Get available feature names",
    responses=names_responses.responses,
)
async def feature_names(response: Response):
    return names_responses(response, 200)(names=Features.names())


# ---------------------------------------------- - - -
# LOAD FEATURE
#

load_feature_responses = ModelResponses(
    {200: Models.Features.Base, 409: Models.Commons.Error}
)


@api.post(
    "/features/load",
    description="Load a feature",
    responses=load_feature_responses.responses,
)
async def load_dev_feature(
    response: Response,
    entry: str = Body(description="Feature name or feature development directory"),
):
    try:
        name, is_started = Features.load(entry)
        return load_feature_responses(response, 200)(name=name, is_started=is_started)
    except KeyError as error:
        return load_feature_responses(response, 409)(message=str(error))
    except ValueError as error:
        return load_feature_responses(response, 409)(message=str(error))
    except Exception as exception:
        return load_feature_responses(response, 409)(message=str(exception))


# ---------------------------------------------- - - -
# UNLOAD FEATURE
#

unload_feature_responses = ModelResponses(
    {200: Models.Features.Base, 404: Models.Commons.Error}
)


@api.post(
    "/features/unload",
    description="Unload a feature",
    responses=unload_feature_responses.responses,
)
async def load_dev_feature(
    response: Response,
    feature_name: str = Body(description="Feature name"),
):
    try:
        await Features.unload(feature_name)
        return unload_feature_responses(response, 200)(
            name=feature_name, is_started=False
        )
    except KeyError as error:
        return unload_feature_responses(response, 404)(message=str(error))
