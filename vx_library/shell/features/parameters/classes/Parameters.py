import os, importlib.util
from types import ModuleType
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


def import_module_from_path(name: str, path: str):
    if not os.path.exists(path):
        return

    module_spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)

    return module


def get_params_from_dev_directory(
    directory: str,
) -> tuple[str, FeatureParams, ModuleType | None, ModuleType | None]:
    feature_name = get_dev_feature_name(directory)

    custom_actions_module = import_module_from_path(
        f"{feature_name}_custom_actions",
        f"{directory}/config/root/{feature_name}/custom_actions.py",
    )
    custom_data_module = import_module_from_path(
        f"{feature_name}_custom_data",
        f"{directory}/config/root/{feature_name}/custom_data.py",
    )
    root_file_path = f"{directory}/config/root/{feature_name}.json"
    user_file_path = f"{directory}/config/user/{feature_name}.json"

    return (
        feature_name,
        FeatureParams.create(root_file_path, user_file_path, True),
        custom_actions_module,
        custom_data_module,
    )


def get_params_from_feature_name(
    feature_name: str,
) -> tuple[FeatureParams, ModuleType | None, ModuleType | None]:
    custom_actions_module = import_module_from_path(
        f"{feature_name}_custom_actions",
        f"{ROOT_PARAMS_DIR}/{feature_name}/custom_actions.py",
    )
    custom_data_module = import_module_from_path(
        f"{feature_name}_custom_data",
        f"{ROOT_PARAMS_DIR}/{feature_name}/custom_data.py",
    )
    root_file_path = f"{ROOT_PARAMS_DIR}/{feature_name}.json"
    user_file_path = f"{USER_PARAMS_DIR}/{feature_name}.json"

    return (
        FeatureParams.create(root_file_path, user_file_path),
        custom_data_module,
        custom_actions_module,
    )


def get_params_from_entry(
    entry: str,
) -> tuple[str, FeatureParams, ModuleType | None, ModuleType | None]:
    if os.path.exists(entry) and os.path.isdir(entry):
        return get_params_from_dev_directory(entry)

    try:
        params, custom_data_module, custom_actions_module = (
            get_params_from_feature_name(entry)
        )
        return entry, params, custom_data_module, custom_actions_module
    except MissingFileError:
        raise ValueError(f"{entry} (Bad entry)")


class Parameters:
    @staticmethod
    def get_root_feature_names() -> list[str]:
        return get_root_feature_names()

    @staticmethod
    def get(
        entry: str,
    ) -> tuple[str, FeatureParams, ModuleType | None, ModuleType | None]:
        return get_params_from_entry(entry)
