from fastapi import Response, Path, Body
from ..api import api
from ..globals import ModelResponses, Models
from ..features import Features

# FEATURE NAMES
names_responses = ModelResponses({200: Models.Features.Names})


@api.get(
    "/features/names",
    description="Get available feature names",
    responses=names_responses.responses,
)
async def feature_names(response: Response):
    return names_responses(response, 200)(names=Features.keys())


# INIT DEV FEATURE
init_dev_responses = ModelResponses(
    {200: Models.Features.Base, 409: Models.Commons.Error}
)


@api.post(
    "/feature/dev/init",
    description="Start feature in development mode",
    responses=init_dev_responses.responses,
)
async def init_dev_feature(
    response: Response, dev_dir: str = Body(description="Development directory")
):
    feature_name, error = Features.init_dev_feature(dev_dir)

    if error:
        return init_dev_responses(response, 409)(message=error)

    return init_dev_responses(response, 200)(name=feature_name)


# STOP DEV FEATURE
stop_dev_responses = ModelResponses(
    {200: Models.Features.Base, 409: Models.Commons.Error}
)


@api.get(
    "/feature/dev/stop",
    description="Stop feature in development mode",
    responses=stop_dev_responses.responses,
)
async def stop_dev_feature(response: Response):
    feature_name, error = await Features.remove_dev_feature()

    if error:
        return stop_dev_responses(response, 409)(message=error)

    return stop_dev_responses(response, 200)(name=feature_name)


# START FEATURE
start_responses = ModelResponses(
    {200: Models.Features.Base, 404: Models.Commons.Error, 409: Models.Commons.Error}
)


@api.get(
    "/feature/{feature_name}/start",
    description="Start a feature",
    responses=start_responses.responses,
)
async def start_feature(
    response: Response,
    feature_name: str = Path(description="Feature name"),
):
    if not Features.key_exists(feature_name):
        return start_responses(response, 404)(
            message=f"Feature '{feature_name}' not found",
            details=Models.Commons.KeyError(key=feature_name),
        )

    feature = Features.get(feature_name)

    if feature.is_started:
        return start_responses(response, 409)(
            message=f"Feature '{feature_name}' is already started",
            details=Models.Features.Base(name=feature_name),
        )

    feature.start()

    return start_responses(response, 200)(name=feature_name)


# STOP FEATURE
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
    if not Features.key_exists(feature_name):
        return stop_responses(response, 404)(
            message=f"Feature '{feature_name}' not found",
            details=Models.Commons.KeyError(key=feature_name),
        )

    feature = Features.get(feature_name)

    if not feature.is_started:
        return stop_responses(response, 409)(
            message=f"Feature '{feature_name}' is not started",
            details=Models.Features.Base(name=feature_name, is_started=False),
        )

    await feature.stop()

    return stop_responses(response, 200)(name=feature_name, is_started=False)


# FEATURE STATE
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
    if not Features.key_exists(feature_name):
        return state_responses(response, 404)(
            message=f"Feature '{feature_name}' not found",
            details=Models.Commons.KeyError(key=feature_name),
        )

    feature = Features.get(feature_name)

    if not feature.is_started:
        return state_responses(response, 409)(
            message=f"Feature '{feature_name}' is not started",
            details=Models.Features.Base(name=feature_name, is_started=False),
        )

    return state_responses(response, 200)(
        name=feature_name, is_started=True, state=feature.state
    )


# LOG LISTENER FEATURE
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
    if not Features.key_exists(feature_name):
        return logListener_responses(response, 404)(
            message=f"Feature '{feature_name}' not found",
            details=Models.Commons.KeyError(key=feature_name),
        )

    feature = Features.get(feature_name)

    if not feature.is_started:
        return logListener_responses(response, 409)(
            message=f"Feature '{feature_name}' is not started",
            details=Models.Features.Base(name=feature_name, is_started=False),
        )

    return logListener_responses(response, 200)(
        name=feature_name, is_started=True, log_listener=feature.listen_logs
    )


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
    if not Features.key_exists(feature_name):
        return toggle_logListener_responses(response, 404)(
            message=f"Feature '{feature_name}' not found",
            details=Models.Commons.KeyError(key=feature_name),
        )

    feature = Features.get(feature_name)

    if not feature.is_started:
        return toggle_logListener_responses(response, 409)(
            message=f"Feature '{feature_name}' is not started",
            details=Models.Features.Base(name=feature_name, is_started=False),
        )

    feature.listen_logs = not feature.listen_logs

    return toggle_logListener_responses(response, 200)(
        name=feature_name, is_started=True, log_listener=feature.listen_logs
    )
