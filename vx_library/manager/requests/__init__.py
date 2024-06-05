import requests
from requests import Response
from ..logger import Logger


def request_get(path: str):
    return requests.get(f"http://localhost:6481{path}")


def request_post(path: str, payload):
    return requests.post(f"http://localhost:6481{path}", json=payload)


def handle_error_response(response: Response):
    if response.status_code == 500:
        Logger.log("Internal server error", "ERROR")
        return

    try:
        error: dict = response.json()

        if error["shell_error"]:
            Logger.log(f"[Shell]: {error['message']}", "ERROR")
        else:
            Logger.log(error["details"], "ERROR")
    except:
        Logger.log("Internal uncaught exception", "ERROR")


class ShellRequests:
    class ShellException(Exception):
        def __init__(self, message: str):
            super().__init__(message)

    @staticmethod
    def check_ping(value: bool):
        def decorator(func):
            def wrapper(*args, **kwargs):
                if ShellRequests.ping() == value:
                    return func(*args, **kwargs)
                else:
                    Logger.log(
                        (
                            "Vixen Shell is not running"
                            if value
                            else "Vixen Shell is already running"
                        ),
                        "WARNING",
                    )
                    return None

            return wrapper

        return decorator

    @staticmethod
    def ping() -> bool:
        try:
            request_get("/ping")
            return True
        except requests.RequestException:
            return False

    @staticmethod
    @check_ping(False)
    def open():
        from ...shell import run_shell

        run_shell()

    @staticmethod
    @check_ping(True)
    def close():
        Logger.log("Close Vixen Shell")
        request_get("/shutdown")

    @staticmethod
    @check_ping(True)
    def load_feature(entry: str) -> str | None:
        response = request_post(f"/features/load", entry)

        if not response.status_code == 200:
            handle_error_response(response)
            return

        return response.json()["name"]

    @staticmethod
    @check_ping(True)
    def unload_feature(feature_name: str) -> str | None:
        response = request_post(f"/features/unload", feature_name)

        if not response.status_code == 200:
            handle_error_response(response)
            return

        return response.json()["name"]

    @staticmethod
    @check_ping(True)
    def feature_names() -> list:
        return request_get("/features/names").json()["names"]

    @staticmethod
    @check_ping(True)
    def start_feature(feature_name: str) -> str | None:
        response = request_get(f"/feature/{feature_name}/start")

        if not response.status_code == 200:
            handle_error_response(response)
            return

        return response.json()["name"]
