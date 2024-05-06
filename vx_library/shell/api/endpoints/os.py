import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import subprocess, threading
from typing import Literal
from fastapi import Response, Path, Body
from fastapi.responses import FileResponse
from ..api import api
from ...globals import ModelResponses, Models

# ---------------------------------------------- - - -
# OS EXEC
#

exec_responses = ModelResponses(
    {
        200: Models.Os.ExecInfo,
        404: Models.Commons.Error,
    }
)


@api.post(
    "/os/run", description="Run linux command", responses=exec_responses.responses
)
async def post_log(
    response: Response,
    command: str = Body(description="Command"),
    args: list[str] = Body(description="Optional command arguments", default=[]),
    wait_process: bool = Body(
        description="Wait for the process to end in a thread (Can solve certain problems with single instance programs e.g. rofi)",
        default=False,
    ),
):
    try:
        process = subprocess.Popen(
            [command] + args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        if wait_process:
            threading.Thread(target=process.wait).start()

        return exec_responses(response, 200)(
            pid=process.pid, command=command, args=args
        )

    except Exception as exception:
        return exec_responses(response, 404)(message=str(exception))


# ---------------------------------------------- - - -
# OS ICONS
#

gtk_icon_size = {
    "16": Gtk.IconSize.BUTTON,
    "24": Gtk.IconSize.LARGE_TOOLBAR,
    "32": Gtk.IconSize.DND,
    "48": Gtk.IconSize.DIALOG,
}


def get_icon_path(icon_name: str, size: Literal[16, 24, 32, 48], color: str = None):
    icon_theme = Gtk.IconTheme.get_default()

    if color:
        icon_name += f"-{color}"

    icon_info = (
        icon_theme.lookup_icon(icon_name, gtk_icon_size[size], 0)
        or icon_theme.lookup_icon("image-missing-symbolic", gtk_icon_size[size], 0)
        or icon_theme.lookup_icon("image-missing", gtk_icon_size[size], 0)
    )

    return icon_info.get_filename()


@api.post("/os/icon/{icon_name}", description="Get a Gtk icon")
async def get_icon(
    icon_name: str = Path(description="Icon name"),
    size: Literal["16", "24", "32", "48"] = Body(description="Icon size", default="48"),
    color: str = Body(description="Optional icone place color", default=None),
):
    return FileResponse(get_icon_path(icon_name, size, color))
