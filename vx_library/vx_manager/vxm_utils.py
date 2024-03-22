import os, requests
from ..vx_shell import api


def sudo_is_used() -> bool:
    return os.geteuid() == 0


def api_is_running() -> bool:
    try:
        response = requests.get("http://localhost:6481/ping")

        if response.status_code == 200:
            return True
        else:
            return False

    except requests.RequestException:
        return False


def close_api() -> bool:
    try:
        response = requests.get("http://localhost:6481/shutdown")

        if response.status_code == 200:
            return True
        else:
            return False

    except requests.RequestException:
        return False


def open_api():
    api.run()
