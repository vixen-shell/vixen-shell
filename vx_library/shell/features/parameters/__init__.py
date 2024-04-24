"""
Author            : Nohavye
Author's Email    : noha.poncelet@gmail.com
Repository        : https://github.com/vixen-shell/vixen-shell.git
Description       : vixen shell api features parameters library.
License           : GPL3
"""

from typing import List
from .parameters import FeatureParams

from .models import (
    LevelKeys,
    AnchorEdgeKeys,
    AlignmentKeys,
    FrameParams,
    LayerFrameParams,
    MarginParams,
)

from ...logger import Logger


class Parameters:
    from ...globals import ROOT_CONFIG_DIRECTORY, USER_CONFIG_DIRECTORY

    ROOT_STARTUP_FILE_PATH = f"{ROOT_CONFIG_DIRECTORY}/startup.json"
    USER_STARTUP_FILE_PATH = f"{USER_CONFIG_DIRECTORY}/startup.json"
    ROOT_PARAMS_DIR = f"{ROOT_CONFIG_DIRECTORY}/features"
    USER_PARAMS_DIR = f"{USER_CONFIG_DIRECTORY}/features"

    @staticmethod
    def read(file_path: str) -> dict | None:
        from .utils import read_json

        return read_json(file_path)

    @staticmethod
    def get_startup_list() -> List[str]:
        list: List[str] = []

        try:
            list.extend(Parameters.read(Parameters.ROOT_STARTUP_FILE_PATH))
            list.extend(Parameters.read(Parameters.USER_STARTUP_FILE_PATH))
        except Exception as exception:
            Logger.log(exception, "ERROR")

        return list

    @staticmethod
    def get_feature_parameters(
        root_file_path: str, user_file_path: str
    ) -> FeatureParams | None:
        try:
            return FeatureParams.create(root_file_path, user_file_path)
        except Exception as exception:
            Logger.log(exception, "WARNING")
            return

    @staticmethod
    def get_feature_parameter_list() -> List[FeatureParams] | None:
        def get_file_names() -> List[str]:
            import os

            list: List[str] = []

            try:
                for file_name in os.listdir(Parameters.ROOT_PARAMS_DIR):
                    if os.path.isfile(
                        f"{Parameters.ROOT_PARAMS_DIR}/{file_name}"
                    ) and file_name.endswith(".json"):
                        list.append(file_name)
            except FileNotFoundError as exception:
                Logger.log(f"{exception.strerror}: {exception.filename}", "WARNING")

            return list

        # feature_parameter_list
        list: List[FeatureParams] = []
        file_names = get_file_names()

        if not file_names:
            return

        for file_name in file_names:
            params = Parameters.get_feature_parameters(
                f"{Parameters.ROOT_PARAMS_DIR}/{file_name}",
                f"{Parameters.USER_PARAMS_DIR}/{file_name}",
            )

            if not params:
                return

            list.append(params)

        return list
