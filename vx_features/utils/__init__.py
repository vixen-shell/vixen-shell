import os
from glob import glob
from vx_path import VxPath


class FeatureUtils:
    @staticmethod
    def is_dev_feature(entry: str):
        return (
            entry not in FeatureUtils.get_root_feature_names()
            and os.path.exists(entry)
            and os.path.isdir(entry)
        )

    @staticmethod
    def feature_name_from(entry: str) -> str:
        def dev_module_name(dev_path: str) -> str:
            root_path = f"{dev_path}/root"
            root_items = [
                item
                for item in os.listdir(root_path)
                if os.path.isdir(f"{root_path}/{item}")
            ]

            if len(root_items) != 1:
                only = "only " if len(root_items) > 1 else ""
                raise Exception(
                    f"Root folder should {only}contain one folder, cannot set feature package"
                )

            return root_items[0]

        return dev_module_name(entry) if FeatureUtils.is_dev_feature(entry) else entry

    @staticmethod
    def sys_path_from(entry: str):
        return (
            [f"{entry}/root"] + glob(f"{entry}/.venv/lib/python*/site-packages")
            if FeatureUtils.is_dev_feature(entry)
            else glob(f"/usr/share/vixen/{entry}.libs")
        )

    @staticmethod
    def user_params_file_from(entry: str):
        if FeatureUtils.is_dev_feature(entry):
            return f"{entry}/user/{FeatureUtils.feature_name_from(entry)}.json"

        return f"{VxPath.USER_FEATURE_PARAMS}/{entry}.json"

    @staticmethod
    def get_root_feature_names():
        feature_names: list[str] = []

        for item in os.listdir(VxPath.ROOT_FEATURE_MODULES):
            path = f"{VxPath.ROOT_FEATURE_MODULES}/{item}"

            if os.path.isdir(path):
                feature_names.append(item)

        return feature_names
