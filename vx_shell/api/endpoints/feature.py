from fastapi import Response, Path, Body
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict
from vx_feature_utils import ParamDataHandler
from typing import Any
from ..api import api
from ...globals import ModelResponses, Models
from ...features import Features


# ---------------------------------------------- - - -
# START FEATURE
#

start_responses = ModelResponses(
    {200: Models.Features.Base, 404: Models.Commons.Error, 409: Models.Commons.Error}
)


@api.get(
    "/feature/{feature_name}/start",
    description="Start a feature",
    responses=start_responses.responses,
)
async def start_feature(
    response: Response, feature_name: str = Path(description="Feature name")
):
    if not Features.exists(feature_name):
        return start_responses(response, 404)(
            message=f"Feature '{feature_name}' not found"
        )

    feature = Features.get(feature_name)

    if feature.is_started:
        return start_responses(response, 409)(
            message=f"Feature '{feature_name}' is already started"
        )

    feature.start()

    return start_responses(response, 200)(name=feature_name)


# ---------------------------------------------- - - -
# STOP FEATURE
#

stop_responses = ModelResponses(
    {200: Models.Features.Base, 404: Models.Commons.Error, 409: Models.Commons.Error}
)


@api.get(
    "/feature/{feature_name}/stop",
    description="Stop a feature",
    responses=stop_responses.responses,
)
async def stop_feature(
    response: Response, feature_name: str = Path(description="Feature name")
):
    if not Features.exists(feature_name):
        return stop_responses(response, 404)(
            message=f"Feature '{feature_name}' not found"
        )

    feature = Features.get(feature_name)

    if not feature.is_started:
        return stop_responses(response, 409)(
            message=f"Feature '{feature_name}' is not started"
        )

    await feature.stop()

    return stop_responses(response, 200)(name=feature_name, is_started=False)


# ---------------------------------------------- - - -
# FEATURE STATE
#

state_responses = ModelResponses(
    {200: Models.Features.State, 404: Models.Commons.Error, 409: Models.Commons.Error}
)


@api.get(
    "/feature/{feature_name}/state",
    description="Get a feature global state",
    responses=state_responses.responses,
)
async def feature_state(
    response: Response, feature_name: str = Path(description="Feature name")
):
    if not Features.exists(feature_name):
        return state_responses(response, 404)(
            message=f"Feature '{feature_name}' not found"
        )

    feature = Features.get(feature_name)

    if not feature.is_started:
        return state_responses(response, 409)(
            message=f"Feature '{feature_name}' is not started"
        )

    if not ParamDataHandler.state_is_enable(feature_name):
        return start_responses(response, 200)(
            name=feature_name, is_started=True, state=None
        )

    return state_responses(response, 200)(
        name=feature_name,
        is_started=True,
        state=ParamDataHandler.get_value(f"{feature_name}.state"),
    )


# ---------------------------------------------- - - -
# FEATURE GET PARAM
#

get_param_responses = ModelResponses(
    {200: dict, 404: Models.Commons.Error, 409: Models.Commons.Error}
)


@api.get(
    "/feature/{feature_name}/get_param/{param_path}",
    description="Get a feature param",
    responses=get_param_responses.responses,
)
async def get_feature_param(
    response: Response,
    feature_name: str = Path(description="Feature name"),
    param_path: str = Path(description="Param path"),
):
    if not Features.exists(feature_name):
        return get_param_responses(response, 404)(
            message=f"Feature '{feature_name}' not found"
        )

    feature = Features.get(feature_name)

    if not feature.is_started:
        return get_param_responses(response, 409)(
            message=f"Feature '{feature_name}' is not started"
        )

    try:
        param_value = ParamDataHandler.get_value(f"{feature_name}.{param_path}")
    except Exception as exception:
        return get_param_responses(response, 409)(message=str(exception))

    return get_param_responses(response, 200)(
        {"feature_name": feature_name, param_path: param_value}
    )


# ---------------------------------------------- - - -
# FEATURE SET PARAM
#

set_param_responses = ModelResponses(
    {200: dict, 404: Models.Commons.Error, 409: Models.Commons.Error}
)


class SetParamData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: Any


@api.post(
    "/feature/{feature_name}/set_param/{param_path}",
    description="Get a feature param",
    responses=set_param_responses.responses,
)
async def set_feature_param(
    response: Response,
    feature_name: str = Path(description="Feature name"),
    param_path: str = Path(description="Param path"),
    param_data: SetParamData = Body(description="Param value"),
):
    if not Features.exists(feature_name):
        return set_param_responses(response, 404)(
            message=f"Feature '{feature_name}' not found"
        )

    feature = Features.get(feature_name)

    if not feature.is_started:
        return set_param_responses(response, 409)(
            message=f"Feature '{feature_name}' is not started"
        )

    try:
        ParamDataHandler.set_value(f"{feature_name}.{param_path}", param_data.value)
    except Exception as exception:
        return set_param_responses(response, 409)(message=str(exception))

    return set_param_responses(response, 200)(
        {"feature_name": feature_name, param_path: param_data.value}
    )


# ---------------------------------------------- - - -
# FEATURE DATA
#

feature_data_responses = ModelResponses(
    {
        200: dict,
        404: Models.Commons.Error,
        409: Models.Commons.Error,
    }
)


class DataHandlerModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    args: list = []


class DataHandler:
    def __init__(self, handler, handler_args: list = []):
        self.handler = handler
        self.handler_args = handler_args

    def get_data(self):
        return self.handler(*self.handler_args)


@api.post(
    "/feature/{feature_name}/data",
    description="Get a feature data",
    responses=feature_data_responses.responses,
)
async def get_data(
    response: Response,
    feature_name: str = Path(description="Feature name"),
    data_handlers: list[DataHandlerModel] = Body(
        description="Data handlers information"
    ),
):
    if not Features.exists(feature_name):
        return feature_data_responses(response, 404)(
            message=f"Feature '{feature_name}' not found"
        )

    feature = Features.get(feature_name)

    handlers: dict[str, DataHandler] = {}
    for handler in data_handlers:
        try:
            handlers[handler.name] = DataHandler(
                feature.content.get("data", handler.name),
                handler.args,
            )
        except KeyError as key_error:
            return feature_data_responses(response, 404)(
                message=f"{key_error} not found in '{feature_name}' feature data handlers"
            )
        except Exception as exception:
            return feature_data_responses(response, 409)(message=str(exception))

    custom_data = {}

    try:
        for name, handler in handlers.items():
            custom_data[name] = handler.get_data()
    except Exception as exception:
        return feature_data_responses(response, 409)(message=str(exception))

    return feature_data_responses(response, 200)(**custom_data)


# ---------------------------------------------- - - -
# FEATURE ACTION
#


class ActionHandlerModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    args: list = []


class ActionHandler:
    def __init__(self, handler, handler_args: list = []):
        self.handler = handler
        self.handler_args = handler_args

    def run(self):
        return self.handler(*self.handler_args)


feature_action_responses = ModelResponses(
    {
        200: dict,
        404: Models.Commons.Error,
        409: Models.Commons.Error,
    }
)


@api.post(
    "/feature/{feature_name}/action",
    description="Run a feature action",
    responses=feature_action_responses.responses,
)
async def get_action(
    response: Response,
    feature_name: str = Path(description="Feature name"),
    action_handler: ActionHandlerModel = Body(description="Action handler information"),
):
    if not Features.exists(feature_name):
        return feature_action_responses(response, 404)(
            message=f"Feature '{feature_name}' not found"
        )

    feature = Features.get(feature_name)

    try:
        handler = ActionHandler(
            feature.content.get("action", action_handler.name), action_handler.args
        )
    except KeyError as key_error:
        return feature_action_responses(response, 404)(
            message=f"{key_error} not found in '{feature_name}' feature action handlers"
        )
    except Exception as exception:
        return feature_action_responses(response, 409)(message=str(exception))

    try:
        returned_data = handler.run()
    except Exception as exception:
        return feature_action_responses(response, 409)(message=str(exception))

    return feature_action_responses(response, 200)(
        **{action_handler.name: returned_data or True}
    )


# ---------------------------------------------- - - -
# FEATURE FILE
#


class FileHandlerModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    args: list = []


class FileHandler:
    def __init__(self, handler, handler_args: list = []):
        self.handler = handler
        self.handler_args = handler_args

    def get_filepath(self) -> str:
        return self.handler(*self.handler_args)


feature_file_responses = ModelResponses(
    {
        404: Models.Commons.Error,
        409: Models.Commons.Error,
    }
)


@api.post(
    "/feature/{feature_name}/file",
    description="Get a feature file",
    responses=feature_file_responses.responses,
)
async def get_file(
    response: Response,
    feature_name: str = Path(description="Feature name"),
    file_handler: FileHandlerModel = Body(description="File handler information"),
):
    if not Features.exists(feature_name):
        return feature_file_responses(response, 404)(
            message=f"Feature '{feature_name}' not found"
        )

    feature = Features.get(feature_name)

    try:
        handler = FileHandler(
            feature.content.get("file", file_handler.name), file_handler.args
        )
    except KeyError as key_error:
        return feature_file_responses(response, 404)(
            message=f"{key_error} not found in '{feature_name}' feature file handlers"
        )
    except Exception as exception:
        return feature_file_responses(response, 409)(message=str(exception))

    try:
        response.status_code = 200
        filepath = handler.get_filepath()
        return FileResponse(filepath)
    except Exception as exception:
        return feature_action_responses(response, 409)(message=str(exception))
