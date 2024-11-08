import asyncio
from fastapi import Response, Path, Body
from pydantic import BaseModel, ConfigDict
from ..api import api
from ..models import ModelResponses, Models
from ...features.frame_view import PopupFrame
from ...features import Features

popup_frame = PopupFrame()

# ---------------------------------------------- - - -
# SHOW POPUP FRAME
#

popup_responses = ModelResponses(
    {200: dict, 404: Models.Commons.Error, 409: Models.Commons.Error}
)


class PopupInfos(BaseModel):
    model_config = ConfigDict(extra="forbid")

    route: str
    monitor_id: int | None = None


@api.post(
    "/popup_frame/{feature_name}/show",
    description="Show a popup frame",
    responses=popup_responses.responses,
)
async def show_popup_frame(
    response: Response,
    feature_name: str = Path(description="Feature name"),
    popup_infos: PopupInfos = Body(description="Popup informations"),
):
    global popup_frame

    feature = Features.get(feature_name)

    if not feature:
        return popup_responses(response, 404)(
            message=f"Feature '{feature_name}' not found"
        )

    if not feature.is_started:
        return popup_responses(response, 409)(
            message=f"Feature '{feature_name}' is not started"
        )

    popup_frame.show(
        feature_name,
        popup_infos.route,
        popup_infos.monitor_id or 0,
        feature.dev_mode,
    )

    return popup_responses(response, 200)(
        {"feature_name": popup_frame.feature_name, "popup_frame": True}
    )


# ---------------------------------------------- - - -
# HIDE POPUP FRAME
#


@api.get(
    "/popup_frame/hide",
    description="Hide a popup frame",
    responses=popup_responses.responses,
)
async def hide_popup_frame(response: Response):
    global popup_frame

    popup_frame.hide()

    return popup_responses(response, 200)(
        {"feature_name": popup_frame.feature_name, "popup_frame": False}
    )
