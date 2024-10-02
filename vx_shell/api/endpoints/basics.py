import os
from fastapi import Response, Path, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional, Literal
from vx_config import VxConfig
from vx_path import VxPath
from ..api import api
from ..models import ModelResponses, Models
from ...servers import ApiServer

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


@api.get("/ping", description="Test API availability")
async def ping():
    return "Vixen Shell API (1.0.0)"


@api.get("/shutdown", description="Close API")
async def close():
    ApiServer.server.should_exit = True
    return


@api.get(
    "/vx_theme",
    description="Return the vixen theme preferences",
)
async def get_vx_theme():
    vx_theme = VxConfig.gtk_fonts()
    vx_theme["ui_scale"] = VxConfig.UI_SCALE
    vx_theme["ui_color"] = VxConfig.UI_COLOR

    return JSONResponse(vx_theme)


get_icon_responses = ModelResponses({404: Models.Commons.Error})


@api.get(
    "/system_icons/{icon_name}",
    description="Get system icons (Return an svg blob)",
    responses=get_icon_responses.responses,
)
async def get_system_icon(
    response: Response, icon_name: str = Path(description="Icon name")
):
    icon_theme = Gtk.IconTheme.get_default()
    icon_info = icon_theme.lookup_icon(icon_name, Gtk.IconSize.DIALOG, 0)

    if not icon_info:
        return get_icon_responses(response, 404)(
            message=f"'{icon_name}' icon not exists"
        )

    icon_filepath = icon_info.get_filename()
    return FileResponse(icon_filepath)


@api.get(
    "/phosphor_icons/{icon_name}/",
    description="Get Phosphor icons (Return an svg blob)",
    responses=get_icon_responses.responses,
)
async def get_phosphor_icon(
    response: Response,
    icon_name: str = Path(description="Icone name"),
    icon_style: Optional[
        Literal["bold", "duotone", "fill", "light", "regular", "thin"]
    ] = Query(default=VxConfig.UI_ICONS, description="Icon style"),
):
    icon_prefix = "" if icon_style == "regular" else f"-{icon_style}"

    icon_filepath = (
        f"{VxPath.ROOT_PHOSPHOR_ICONS}/{icon_style}/{icon_name}{icon_prefix}.svg"
    )

    if not os.path.exists(icon_filepath):
        return get_icon_responses(response, 404)(
            message=f"'{icon_name}' icon not exists"
        )

    return FileResponse(icon_filepath)
