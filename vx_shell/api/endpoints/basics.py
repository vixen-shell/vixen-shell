from fastapi.responses import JSONResponse
from vx_config import VxConfig
from ..api import api
from ...servers import ApiServer


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
