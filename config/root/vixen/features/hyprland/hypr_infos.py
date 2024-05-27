import subprocess, json
from . import content


def hypr_info(info_id: str):
    result = subprocess.run(
        f"hyprctl {info_id} -j", shell=True, capture_output=True, text=True
    )

    if result.returncode != 0:
        raise Exception(result.stderr)

    try:
        return json.loads(result.stdout)
    except:
        return result.stdout


@content.add("data")
def version():
    return hypr_info("version")


@content.add("data")
def monitors():
    return hypr_info("monitors")


@content.add("data")
def workspaces():
    return hypr_info("workspaces")


@content.add("data")
def activeworkspace():
    return hypr_info("activeworkspace")


@content.add("data")
def workspacerules():
    return hypr_info("workspacerules")


@content.add("data")
def clients():
    return hypr_info("clients")


@content.add("data")
def devices():
    return hypr_info("devices")


@content.add("data")
def binds():
    return hypr_info("binds")


@content.add("data")
def activewindow():
    return hypr_info("activewindow")


@content.add("data")
def layers():
    return hypr_info("layers")


@content.add("data")
def splash():
    return hypr_info("splash")


@content.add("data")
def cursorpos():
    return hypr_info("cursorpos")


@content.add("data")
def animations():
    return hypr_info("animations")


@content.add("data")
def instances():
    return hypr_info("instances")


@content.add("data")
def layouts():
    return hypr_info("layouts")


@content.add("data")
def rollinglog():
    return hypr_info("rollinglog")
