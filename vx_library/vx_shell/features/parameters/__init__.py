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

from ...log import Logger


class Parameters:
    from ...globals import ROOT_CONFIG_DIRECTORY, USER_CONFIG_DIRECTORY

    ROOT_STARTUP_FILE_PATH = f"{ROOT_CONFIG_DIRECTORY}/startup.json"
    USER_STARTUP_FILE_PATH = f"{USER_CONFIG_DIRECTORY}/startup.json"
    ROOT_FEATURES_DIR = f"{ROOT_CONFIG_DIRECTORY}/features"
    USER_FEATURES_DIR = f"{USER_CONFIG_DIRECTORY}/features"

    @staticmethod
    def get_startup_list() -> List[str]:
        from .utils import read_json

        list: List[str] = []

        try:
            list.extend(read_json(Parameters.ROOT_STARTUP_FILE_PATH))
            list.extend(read_json(Parameters.USER_STARTUP_FILE_PATH))
        except Exception as e:
            Logger.log("ERROR", e)

        return list

    @staticmethod
    def get_feature_parameter_list() -> List[FeatureParams] | None:
        from pydantic import ValidationError

        def get_file_names() -> List[str]:
            import os

            list: List[str] = []

            try:
                for file_name in os.listdir(Parameters.ROOT_FEATURES_DIR):
                    if os.path.isfile(
                        f"{Parameters.ROOT_FEATURES_DIR}/{file_name}"
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
