from fastapi.responses import JSONResponse
from ..api import api
from ...servers import ApiServer


@api.get("/ping", description="Test API availability")
async def ping():
    return "Vixen Shell API (1.0.0)"


@api.get("/shutdown", description="Close API")
async def close():
    ApiServer.server.should_exit = True
    return


import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


@api.get(
    "/prefer_dark_theme",
    description="Return the 'gtk-application-prefer-dark-theme' gtk property",
)
async def prefer_dark_theme():
    settings = Gtk.Settings.get_default()

    return JSONResponse(settings.get_property("gtk-application-prefer-dark-theme"))
