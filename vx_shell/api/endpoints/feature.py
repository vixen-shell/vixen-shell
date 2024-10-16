from fastapi import Response, Path, Body
from pydantic import BaseModel, ConfigDict
from typing import Any
from vx_features import ParamDataHandler, RootContents
from vx_logger import Logger
from vx_gtk import ContextMenuHandler
from ..api import api
from ..models import ModelResponses, Models
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
        try:
            return self.handler(*self.handler_args)
        except Exception as exception:
            Logger.log_exception(exception)
            raise exception


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
                feature.contents.get("data", handler.name),
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
# FEATURE ACTION NAMES
#

action_name_responses = ModelResponses(
    {200: list, 404: Models.Commons.Error, 409: Models.Commons.Error}
)


@api.get(
    "/feature/{feature_name}/actions",
    description="Get the action names of a feature",
    responses=action_name_responses.responses,
)
async def task_names(
    response: Response,
    feature_name: str = Path(description="Feature name"),
):
    if not Features.exists(feature_name):
        return action_name_responses(response, 404)(
            message=f"Feature '{feature_name}' not found"
        )

    feature = Features.get(feature_name)

    if not feature.is_started:
        return action_name_responses(response, 409)(
            message=f"Feature '{feature_name}' is not started"
        )

    return action_name_responses(response, 200)(
        list(RootContents(feature_name).task.__dict__.keys())
    )


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
            feature.contents.get("task", action_handler.name),
            action_handler.args,
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
# FEATURE TOOLTIP
#


class TooltipInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frame_id: str
    text: str


tooltip_responses = ModelResponses(
    {
        200: dict,
        404: Models.Commons.Error,
        409: Models.Commons.Error,
    }
)


@api.post(
    "/feature/{feature_name}/tooltip",
    description="Show tooltip",
    responses=tooltip_responses.responses,
)
async def show_tooltip(
    response: Response,
    feature_name: str = Path(description="Feature name"),
    tooltip_info: TooltipInfo = Body(description="Menu information"),
):
    if not Features.exists(feature_name):
        return tooltip_responses(response, 404)(
            message=f"Feature '{feature_name}' not found"
        )

    feature = Features.get(feature_name)

    try:
        feature.show_tooltip(tooltip_info.frame_id, tooltip_info.text)
    except Exception as exception:
        return menu_responses(response, 409)(message=str(exception))

    return menu_responses(response, 200)(tooltip_info.model_dump())


# ---------------------------------------------- - - -
# FEATURE MENU
#


class MenuInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frame_id: str
    menu_name: str


menu_responses = ModelResponses(
    {
        200: dict,
        404: Models.Commons.Error,
        409: Models.Commons.Error,
    }
)


@api.post(
    "/feature/{feature_name}/menu",
    description="Popup menu",
    responses=menu_responses.responses,
)
async def popup_menu(
    response: Response,
    feature_name: str = Path(description="Feature name"),
    menu_info: MenuInfo = Body(description="Menu information"),
):
    if not Features.exists(feature_name):
        return menu_responses(response, 404)(
            message=f"Feature '{feature_name}' not found"
        )

    feature = Features.get(feature_name)

    try:
        menu_handler = ContextMenuHandler(
            feature.contents.get("menu", menu_info.menu_name)()
        )
    except KeyError as key_error:
        return menu_responses(response, 404)(
            message=f"{key_error} not found in '{feature_name}' feature menu handlers"
        )
    except Exception as exception:
        print(exception)
        return menu_responses(response, 409)(message=str(exception))

    try:
        feature.popup_context_menu(menu_info.frame_id, menu_handler.menu)
    except Exception as exception:
        return menu_responses(response, 409)(message=str(exception))

    return menu_responses(response, 200)(menu_info.model_dump())


# ---------------------------------------------- - - -
# FEATURE DBUS MENU
#


class DbusMenuInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frame_id: str
    service_name: str


dbus_menu_responses = ModelResponses(
    {
        200: dict,
        404: Models.Commons.Error,
        409: Models.Commons.Error,
    }
)


@api.post(
    "/feature/{feature_name}/dbus_menu",
    description="Popup Dbus menu",
    responses=dbus_menu_responses.responses,
)
async def popup_dbus_menu(
    response: Response,
    feature_name: str = Path(description="Feature name"),
    menu_info: DbusMenuInfo = Body(description="Dbus menu information"),
):
    if not Features.exists(feature_name):
        return dbus_menu_responses(response, 404)(
            message=f"Feature '{feature_name}' not found"
        )

    feature = Features.get(feature_name)

    try:
        feature.popup_dbus_menu(menu_info.frame_id, menu_info.service_name)
    except Exception as exception:
        return dbus_menu_responses(response, 409)(message=str(exception))

    return dbus_menu_responses(response, 200)(menu_info.model_dump())
