import os, json, mimetypes
from .FeatureParams import FeatureParams
from ....globals import ROOT_CONFIG_DIRECTORY, USER_CONFIG_DIRECTORY

ROOT_PARAMS_DIR = f"{ROOT_CONFIG_DIRECTORY}/features"
USER_PARAMS_DIR = f"{USER_CONFIG_DIRECTORY}/features"


class ParamsFiles:
    @staticmethod
    def read(file_path: str) -> dict | None:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Unable to found '{file_path}'")

        if (
            not os.path.isfile(file_path)
            or mimetypes.guess_type(file_path)[0] != "application/json"
        ):
            raise ValueError(f"'{file_path}' is not a JSON file")

        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def get_feature_names():
        feature_names: list[str] = []

        for filename in os.listdir(ROOT_PARAMS_DIR):
            filepath = f"{ROOT_PARAMS_DIR}/{filename}"

            if os.path.isfile(filepath) and filename.endswith(".json"):
                feature_names.append(filename[:-5])

        return feature_names

    @staticmethod
    def get_dev_feature_name(dev_directory: str):
        package = ParamsFiles.read(f"{dev_directory}/package.json")
        feature_name = package.get("name")

        if not feature_name:
            raise Exception("Unable to found 'name' property in 'package.json' file")

        feature_name = feature_name.replace("vx-feature-", "")
        return feature_name

    @staticmethod
    def get_params_from_dev_directory(directory: str) -> tuple[str, FeatureParams]:
        name = ParamsFiles.get_dev_feature_name(directory)

        root_file_path = f"{directory}/config/root/{name}.json"
        user_file_path = f"{directory}/config/user/{name}.json"

        return name, FeatureParams.create(root_file_path, user_file_path, True)

    @staticmethod
    def get_params_from_feature_name(name: str) -> FeatureParams:
        root_file_path = f"{ROOT_PARAMS_DIR}/{name}.json"
        user_file_path = f"{USER_PARAMS_DIR}/{name}.json"

        return FeatureParams.create(root_file_path, user_file_path)
