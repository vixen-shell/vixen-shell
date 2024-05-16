import os, json


def read_json(file_path: str) -> dict | None:
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)


def write_json(file_path: str, data: dict):
    if os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    else:
        with open(file_path, "x", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
