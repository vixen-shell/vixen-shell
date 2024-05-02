import os
from .FeatureParams import FeatureParams
from .ParamsBuilder import MissingFileError
from ..utils import read_json
from ....globals import ROOT_CONFIG_DIRECTORY, USER_CONFIG_DIRECTORY

ROOT_PARAMS_DIR = f"{ROOT_CONFIG_DIRECTORY}/features"
USER_PARAMS_DIR = f"{USER_CONFIG_DIRECTORY}/features"


def get_root_feature_names():
    feature_names: list[str] = []

    for filename in os.listdir(ROOT_PARAMS_DIR):
        filepath = f"{ROOT_PARAMS_DIR}/{filename}"

        if os.path.isfile(filepath) and filename.endswith(".json"):
            feature_names.append(filename[:-5])

    return feature_names


def get_dev_feature_name(dev_directory: str):
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


def get_params_from_dev_directory(directory: str) -> tuple[str, FeatureParams]:
    feature_name = get_dev_feature_name(directory)

    root_file_path = f"{directory}/config/root/{feature_name}.json"
    user_file_path = f"{directory}/config/user/{feature_name}.json"

    return feature_name, FeatureParams.create(root_file_path, user_file_path, True)


def get_params_from_feature_name(name: str) -> FeatureParams:
    root_file_path = f"{ROOT_PARAMS_DIR}/{name}.json"
    user_file_path = f"{USER_PARAMS_DIR}/{name}.json"

    return FeatureParams.create(root_file_path, user_file_path)


def get_params_from_entry(entry: str) -> tuple[str, FeatureParams]:
    if os.path.exists(entry) and os.path.isdir(entry):
        return get_params_from_dev_directory(entry)

    try:
        return entry, get_params_from_feature_name(entry)
    except MissingFileError:
        raise ValueError(f"{entry} (Bad entry)")


class Parameters:
    @staticmethod
    def get_root_feature_names() -> list[str]:
        return get_root_feature_names()

    @staticmethod
    def get(entry: str) -> tuple[str, FeatureParams]:
        return get_params_from_entry(entry)
