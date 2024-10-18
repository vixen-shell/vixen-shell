import os, mimetypes
from fastapi import Response, Path, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional, Literal
from vx_config import VxConfig
from vx_path import VxPath
from vx_gtk import Gtk
from ..api import api
from ..models import ModelResponses, Models
from ...servers import ApiServer


@api.get("/ping", description="Test API availability")
async def ping():
    return "Vixen Shell API (1.0.0)"


@api.get("/shutdown", description="Close API")
async def close():
    ApiServer.server.should_exit = True
    return


@api.get(
    "/gtk_fonts",
    description="Return the gtk fonts preferences",
)
async def get_gtk_fonts():
    return JSONResponse(VxConfig.gtk_fonts())


get_file_responses = ModelResponses(
    {
        404: Models.Commons.Error,
        409: Models.Commons.Error,
    }
)


@api.get(
    "/vx_state",
    description="Return the vixen state",
)
async def get_vx_state():
    return JSONResponse(VxConfig.STATE)


@api.get(
    "/system_icons/{icon_name}",
    description="Get system icons (Return an svg blob)",
    responses=get_file_responses.responses,
)
async def get_system_icon(
    response: Response, icon_name: str = Path(description="Icon name")
):
    icon_theme = Gtk.IconTheme.get_default()
    icon_info = icon_theme.lookup_icon(icon_name, Gtk.IconSize.DIALOG, 0)

    if not icon_info:
        return get_file_responses(response, 404)(
            message=f"'{icon_name}' icon not exists"
        )

    icon_filepath = icon_info.get_filename()

    if mimetypes.guess_type(icon_filepath)[0] != "image/svg+xml":
        return get_file_responses(response, 409)(
            message=f"'{icon_name}' not an SVG icon"
        )

    return FileResponse(icon_filepath)


@api.get(
    "/phosphor_icons/{icon_name}/",
    description="Get Phosphor icons (Return an svg blob)",
    responses=get_file_responses.responses,
)
async def get_phosphor_icon(
    response: Response,
    icon_name: str = Path(description="Icone name"),
    icon_style: Optional[
        Literal["bold", "duotone", "fill", "light", "regular", "thin"]
    ] = Query(default=VxConfig.STATE["vx_ui_icons"], description="Icon style"),
):
    icon_prefix = "" if icon_style == "regular" else f"-{icon_style}"

    icon_filepath = (
        f"{VxPath.ROOT_PHOSPHOR_ICONS}/{icon_style}/{icon_name}{icon_prefix}.svg"
    )

    if not os.path.exists(icon_filepath):
        return get_file_responses(response, 404)(
            message=f"'{icon_name}' icon not exists"
        )

    if mimetypes.guess_type(icon_filepath)[0] != "image/svg+xml":
        return get_file_responses(response, 409)(
            message=f"'{icon_name}' not an SVG icon"
        )

    return FileResponse(icon_filepath)


supported_image_file_type = [
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/svg+xml",
    "image/webp",
    "image/x-icon",
    "image/bmp",
    "image/tiff",
]


@api.get(
    "/image_file/",
    description="Get a local file",
    responses=get_file_responses.responses,
)
async def get_image_file(
    response: Response, filepath: str = Query(description="Image file path")
):
    if not os.path.exists(filepath):
        return get_file_responses(response, 404)(
            message=f"Image file '{filepath}' not exists"
        )

    if not mimetypes.guess_type(filepath)[0] in supported_image_file_type:
        return get_file_responses(response, 409)(
            message=f"'{filepath}' is not a supported image file type"
        )

    return FileResponse(filepath)
