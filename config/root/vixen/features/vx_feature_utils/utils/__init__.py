import os, json

# ROOT_PARAMS_DIRECTORY = f"/usr/share/vixen/features"
# USER_PARAMS_DIRECTORY = f"{os.path.expanduser('~')}/.config/vixen/features"
ROOT_PARAMS_DIRECTORY = (
    "/home/noha/Workflow/final/vixen-shell/config/root/vixen/features"
)
USER_PARAMS_DIRECTORY = (
    "/home/noha/Workflow/final/vixen-shell/config/user/vixen/features"
)


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


def get_dev_feature_name(dev_directory: str) -> str:
    package = read_json(f"{dev_directory}/package.json")

    if not package:
        raise Exception(f"Unable to found 'package.json' file '{dev_directory}'")

    feature_name = package.get("name")

    if not feature_name:
        raise Exception(
            f"Unable to found 'name' property in '{dev_directory}/package.json' file"
        )

    feature_name = feature_name.replace("vx-feature-", "")
    return feature_name
