from fastapi import Response, Body
from pydantic import BaseModel, ConfigDict
from ..api import api
from ..models import ModelResponses, Models
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


class LoadFeatureEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entry: str
    tty_path: str = None


load_feature_responses = ModelResponses(
    {200: Models.Features.Base, 409: Models.Commons.Error}
)


@api.post(
    "/features/load",
    description="Load a feature",
    responses=load_feature_responses.responses,
)
async def load_feature(
    response: Response,
    entry: LoadFeatureEntry = Body(
        description="Feature name or feature development directory"
    ),
):
    feature_entry = entry.entry
    tty_path = entry.tty_path

    try:
        name, is_started = Features.load(feature_entry, tty_path)
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


class UnloadFeatureEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    feature_name: str
    for_remove: bool = False


unload_feature_responses = ModelResponses(
    {200: Models.Features.Base, 404: Models.Commons.Error}
)


@api.post(
    "/features/unload",
    description="Unload a feature",
    responses=unload_feature_responses.responses,
)
async def unload_feature(
    response: Response,
    entry: UnloadFeatureEntry = Body(description="Feature name"),
):
    feature_name = entry.feature_name
    for_remove = entry.for_remove

    try:
        await Features.unload(feature_name, for_remove)
        return unload_feature_responses(response, 200)(
            name=feature_name, is_started=False
        )
    except KeyError as error:
        return unload_feature_responses(response, 404)(message=str(error))
