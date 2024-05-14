import os, importlib
from vx_feature_utils import FeatureContent
from .FeatureParams import FeatureParams
from ..utils import read_json
from ....globals import ROOT_CONFIG_DIRECTORY, USER_CONFIG_DIRECTORY

ROOT_PARAMS_DIR = f"{ROOT_CONFIG_DIRECTORY}/features"
USER_PARAMS_DIR = f"{USER_CONFIG_DIRECTORY}/features"


def get_root_feature_names():
    feature_names: list[str] = []

    for item in os.listdir(ROOT_PARAMS_DIR):
        path = f"{ROOT_PARAMS_DIR}/{item}"

        if os.path.isdir(path):
            feature_names.append(item)

    feature_names.remove("vx_feature_utils")
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


def get_params_from_dev_directory(
    directory: str,
) -> tuple[str, FeatureParams, FeatureContent]:
    feature_name = get_dev_feature_name(directory)

    module = importlib.import_module(feature_name)
    feature_content: FeatureContent = module.feature

    params = FeatureParams.create(
        feature_content.root_params_dict,
        f"{directory}/config/user/{feature_name}.json",
        True,
    )

    return feature_name, params, module


def get_params_from_feature_name(
    feature_name: str,
) -> tuple[FeatureParams, FeatureContent]:

    module = importlib.import_module(feature_name)
    feature_content: FeatureContent = module.feature

    params = FeatureParams.create(
        feature_content.root_params_dict,
        f"{USER_PARAMS_DIR}/{feature_name}.json",
    )

    return params, feature_content


def get_params_from_entry(
    entry: str,
) -> tuple[str, FeatureParams, FeatureContent]:
    if os.path.exists(entry) and os.path.isdir(entry):
        return get_params_from_dev_directory(entry)

    params, feature_content = get_params_from_feature_name(entry)
    return entry, params, feature_content


class Parameters:
    @staticmethod
    def get_root_feature_names() -> list[str]:
        return get_root_feature_names()

    @staticmethod
    def get(
        entry: str,
    ) -> tuple[str, FeatureParams, FeatureContent]:
        return get_params_from_entry(entry)
