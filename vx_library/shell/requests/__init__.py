import requests
from ..globals import API_PORT


def request_get(path: str):
    return requests.get(f"http://localhost:{API_PORT}{path}")


def request_post(path: str, payload):
    return requests.post(f"http://localhost:{API_PORT}{path}", json=payload)


class ApiRequests:
    @staticmethod
    def ping() -> bool:
        try:
            request_get("/ping")
            return True
        except requests.RequestException:
            return False

    @staticmethod
    def close():
        try:
            request_get("/shutdown")

        except requests.RequestException:
            raise Exception("API is not responding")

    @staticmethod
    def init_dev_feature(dev_dir: str) -> str:
        try:
            response = request_post("/feature/dev/init", dev_dir)

            if not response.status_code == 200:
                raise Exception(response.json()["message"])

            return response.json()["name"]

        except requests.RequestException:
            raise Exception("API is not responding")

    @staticmethod
    def stop_dev_feature():
        try:
            response = request_get("/feature/dev/stop")

            if not response.status_code == 200:
                raise Exception(response.json()["message"])

        except requests.RequestException:
            raise Exception("API is not responding")

    @staticmethod
    def feature_names() -> list:
        try:
            return request_get("/features/names").json()["names"]

        except requests.RequestException:
            raise Exception("API is not responding")

    @staticmethod
    def start_feature(feature_name: str) -> str:
        try:
            response = request_get(f"/feature/{feature_name}/start")

            if not response.status_code == 200:
                raise Exception(response.json()["message"])

            return response.json()["name"]

        except requests.RequestException as error:
            raise Exception("API is not responding")
