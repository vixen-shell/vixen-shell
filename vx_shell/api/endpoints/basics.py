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
    "/gtk_default_font",
    description="Return the gtk default font name and size",
)
async def gtk_default_font():
    settings = Gtk.Settings.get_default()
    default_font = settings.get_property("gtk-font-name").rsplit(" ", 1)

    font_family = default_font[0]
    font_size = int(default_font[1])

    return JSONResponse(
        {
            "font_family": font_family,
            "font_size": font_size,
        }
    )


@api.get(
    "/gtk_dark_theme",
    description="Return the gtk 'prefer-dark-theme' property",
)
async def gtk_dark_theme():
    settings = Gtk.Settings.get_default()
    dark_theme = settings.get_property("gtk-application-prefer-dark-theme")

    return JSONResponse(dark_theme)
