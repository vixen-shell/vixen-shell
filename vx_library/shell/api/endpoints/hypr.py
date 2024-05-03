import subprocess, json
from fastapi import Response, Path
from typing import Literal
from ..api import api
from ...globals import ModelResponses, Models

# ---------------------------------------------- - - -
# HYPR INFO
#

info_responses = ModelResponses({200: dict, 404: Models.Commons.Error})


@api.get(
    "/hypr/info/{info_id}",
    description="Get Hyprland informations",
    responses=info_responses.responses,
)
async def feature_names(
    response: Response,
    info_id: Literal[
        "version",
        "monitors",
        "workspaces",
        "activeworkspace",
        "workspacerules",
        "clients",
        "devices",
        "binds",
        "activewindow",
        "layers",
        "splash",
        "cursorpos",
        "animations",
        "instances",
        "layouts",
        "rollinglog",
    ] = Path(description="Information Id"),
):
    result = subprocess.run(
        f"hyprctl {info_id} -j", shell=True, capture_output=True, text=True
    )

    if result.returncode != 0:
        return info_responses(response, 404)(message="Unable to access query")

    try:
        data = json.loads(result.stdout)
    except:
        data = result.stdout

    return info_responses(response, 200)({info_id: data})
