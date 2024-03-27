import sys, os, json
from typing import List
from pydantic import ValidationError
from .parameters import FeatureParams
from ...globals import ROOT_CONFIG_DIRECTORY, USER_CONFIG_DIRECTORY
from ...log import Logger


class Parameters:
    @staticmethod
    def get_startup_list() -> List[str]:
        def get_startup_params(config_directory: str) -> List[str]:
            with open(
                f"{config_directory}/startup.json", "r", encoding="utf-8"
            ) as file:
                return json.load(file)

        list: List[str] = []

        try:
            list.extend(get_startup_params(ROOT_CONFIG_DIRECTORY))
            list.extend(get_startup_params(USER_CONFIG_DIRECTORY))
        except Exception as e:
            Logger.log("ERROR", e)

        return list

    @staticmethod
    def get_feature_parameter_list() -> List[FeatureParams] | None:
        def get_file_names() -> List[str]:
            list: List[str] = []

            try:
                for file_name in os.listdir(f"{ROOT_CONFIG_DIRECTORY}/features"):
                    if os.path.isfile(
                        f"{ROOT_CONFIG_DIRECTORY}/features/{file_name}"
                    ) and file_name.endswith(".json"):
                        list.append(file_name)
            except FileNotFoundError as e:
                Logger.log("WARNING", f"{e.strerror}: {e.filename}")

            return list

        # feature_parameter_list
        list: List[FeatureParams] = []
        file_names = get_file_names()

        if not file_names:
            return

        for file_name in file_names:
            try:
                list.append(FeatureParams.create(file_name))
            except ValidationError as e:
                error = e.errors()[0]
                Logger.log("WARNING", f"File: '{file_name}'")
                Logger.log(
                    "WARNING",
                    f"{error['type']}: {error['loc']}, {error['msg']}",
                )
                Logger.log("ERROR", "Feature not initialized!")
                return

        return list
