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
            Logger.log(f"{error['message']}", "ERROR")
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
        from vx_shell import run_shell

        run_shell()

    @staticmethod
    @check_ping(True)
    def close():
        Logger.log("Close Vixen Shell")
        request_get("/shutdown")

    @staticmethod
    def log_to_tty(tty_path: str):
        return request_post("/log_to_tty", tty_path)

    @staticmethod
    def unlog_to_tty(tty_path: str):
        return request_post("/unlog_to_tty", tty_path)

    @staticmethod
    @check_ping(True)
    def feature_names() -> list[str] | None:
        return request_get("/features/names").json()["names"]

    @staticmethod
    @check_ping(True)
    def load_feature(entry: str, tty_path: str = None) -> str | None:
        load_entry = {"entry": entry}

        if tty_path:
            load_entry["tty_path"] = tty_path

        response = request_post(f"/features/load", load_entry)

        if not response.status_code == 200:
            handle_error_response(response)
            return

        return response.json()["name"]

    @staticmethod
    @check_ping(True)
    def unload_feature(feature_name: str, for_remove: bool = False) -> str | None:
        response = request_post(
            f"/features/unload",
            {"feature_name": feature_name, "for_remove": for_remove},
        )

        if not response.status_code == 200:
            handle_error_response(response)
            return

        return response.json()["name"]

    @staticmethod
    @check_ping(True)
    def start_feature(feature_name: str) -> str | None:
        response = request_get(f"/feature/{feature_name}/start")

        if not response.status_code == 200:
            handle_error_response(response)
            return

        return response.json()["name"]

    @staticmethod
    @check_ping(True)
    def stop_feature(feature_name: str) -> str | None:
        response = request_get(f"/feature/{feature_name}/stop")

        if not response.status_code == 200:
            handle_error_response(response)
            return

        return response.json()["name"]

    @staticmethod
    @check_ping(True)
    def feature_frame_ids(feature_name: str) -> dict | None:
        response = request_get(f"/frames/{feature_name}/ids")

        if not response.status_code == 200:
            handle_error_response(response)
            return

        return response.json()

    @staticmethod
    @check_ping(True)
    def toggle_feature_frame(feature_name: str, frame_id: str) -> str | None:
        response = request_get(f"/frame/{feature_name}/toggle/{frame_id}")

        if not response.status_code == 200:
            handle_error_response(response)
            return

        return response.json()["id"]

    @staticmethod
    @check_ping(True)
    def open_feature_frame(feature_name: str, frame_id: str) -> str | None:
        response = request_get(f"/frame/{feature_name}/open/{frame_id}")

        if not response.status_code == 200:
            handle_error_response(response)
            return

        return response.json()["id"]

    @staticmethod
    @check_ping(True)
    def close_feature_frame(feature_name: str, frame_id: str) -> str | None:
        response = request_get(f"/frame/{feature_name}/close/{frame_id}")

        if not response.status_code == 200:
            handle_error_response(response)
            return

        return response.json()["id"]

    @staticmethod
    @check_ping(True)
    def feature_task_names(feature_name: str) -> list | None:
        response = request_get(f"/feature/{feature_name}/actions")

        if not response.status_code == 200:
            handle_error_response(response)
            return

        return response.json()

    @staticmethod
    @check_ping(True)
    def run_feature_task(
        feature_name: str, task_name: str, args: list = []
    ) -> str | None:
        payload = {"name": task_name, "args": args}

        response = request_post(f"/feature/{feature_name}/action", payload)

        if not response.status_code == 200:
            handle_error_response(response)
            return

        return response.json()[task_name]
