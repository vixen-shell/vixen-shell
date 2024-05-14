from fastapi import Response, Path, Body
from pydantic import BaseModel
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

    return state_responses(response, 200)(
        name=feature_name, is_started=True, state=feature.state
    )


# ---------------------------------------------- - - -
# LOG LISTENER FEATURE
#

logListener_responses = ModelResponses(
    {
        200: Models.Features.LogListener,
        404: Models.Commons.Error,
        409: Models.Commons.Error,
    }
)


@api.get(
    "/feature/{feature_name}/log_listener",
    description="Get feature log listener state",
    responses=logListener_responses.responses,
)
async def feature_log_listener_state(
    response: Response, feature_name: str = Path(description="Feature name")
):
    if not Features.exists(feature_name):
        return logListener_responses(response, 404)(
            message=f"Feature '{feature_name}' not found"
        )

    feature = Features.get(feature_name)

    if not feature.is_started:
        return logListener_responses(response, 409)(
            message=f"Feature '{feature_name}' is not started"
        )

    return logListener_responses(response, 200)(
        name=feature_name, is_started=True, log_listener=feature.listen_logs
    )


# ---------------------------------------------- - - -
# TOGGLE LOG LISTENER
#

toggle_logListener_responses = ModelResponses(
    {
        200: Models.Features.LogListener,
        404: Models.Commons.Error,
        409: Models.Commons.Error,
    }
)


@api.get(
    "/feature/{feature_name}/log_listener/toggle",
    description="Toogle feature log listener state",
    responses=toggle_logListener_responses.responses,
)
async def toggle_feature_log_listener_state(
    response: Response, feature_name: str = Path(description="Feature name")
):
    if not Features.exists(feature_name):
        return toggle_logListener_responses(response, 404)(
            message=f"Feature '{feature_name}' not found"
        )

    feature = Features.get(feature_name)

    if not feature.is_started:
        return toggle_logListener_responses(response, 409)(
            message=f"Feature '{feature_name}' is not started"
        )

    feature.listen_logs = not feature.listen_logs

    return toggle_logListener_responses(response, 200)(
        name=feature_name, is_started=True, log_listener=feature.listen_logs
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
    name: str
    args: list = []


class DataHandler:
    def __init__(self, handler, handler_args: list = []):
        self.handler = handler
        self.handler_args = handler_args

    def get_data(self):
        return self.handler(*self.handler_args)


@api.post("/feature/{feature_name}/data", description="Get a feature data")
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
                feature.data_handlers[handler.name],
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
