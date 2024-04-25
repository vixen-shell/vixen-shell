import os

# ---------------------------------------------- - - -
# PORTS

API_PORT = 6481
FRONT_PORT = 6492
FRONT_DEV_PORT = 5173

# ---------------------------------------------- - - -
# PATH

HOME_DIRECTORY = os.path.expanduser("~")
USER_CONFIG_DIRECTORY = f"{HOME_DIRECTORY}/.config/vixen"
ROOT_CONFIG_DIRECTORY = f"/usr/share/vixen"
FRONT_DIST_DIRECTORY = "/var/opt/vx-front-main/dist"

# ---------------------------------------------- - - -
# UTILS


def get_front_port(dev_mode: bool):
    return FRONT_PORT if not dev_mode else FRONT_DEV_PORT


def get_frame_uri(feature_name: str, client_id: str, route: str, dev_mode: bool):
    def get_params():
        feature_param = f"feature={feature_name}"
        client_id_param = f"client_id={client_id}"
        route_param = f"route={route}"

        return f"{feature_param}&{client_id_param}&{route_param}"

    return f"http://localhost:{get_front_port(dev_mode)}/?{get_params()}"
