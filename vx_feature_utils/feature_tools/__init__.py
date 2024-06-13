import os, sys, importlib, glob
from ..feature_params import root_FeatureParams_dict


class Utils:
    from .classes import FeatureUtils, FeatureContent, FeatureContentReference

    @staticmethod
    def define_feature_utils():
        return Utils.FeatureUtils()

    @staticmethod
    def define_feature_content(
        root_params_dict: root_FeatureParams_dict = {},
    ) -> FeatureContentReference:
        from inspect import stack, getmodule

        return Utils.FeatureContent(
            getmodule(stack()[1][0]).__package__, root_params_dict
        )

    @staticmethod
    def get_root_feature_names():
        root_params_directory = "/usr/share/vixen/features"

        feature_names: list[str] = []

        for item in os.listdir(root_params_directory):
            path = f"{root_params_directory}/{item}"

            if os.path.isdir(path):
                feature_names.append(item)

        return feature_names

    @staticmethod
    def get_dev_feature_name(dev_directory):
        root_params_directory = f"{dev_directory}/root"

        for item in os.listdir(root_params_directory):
            path = f"{root_params_directory}/{item}"

            if os.path.isdir(path):
                return item

    @staticmethod
    def get_feature_content(entry: str):
        sys_path = None

        if os.path.exists(entry) and os.path.isdir(entry):
            sys_path = [f"{entry}/root"]
            site_packages_dir = glob.glob(f"{entry}/.venv/lib/python*/site-packages")
            sys_path.extend(site_packages_dir)
            feature_name = Utils.get_dev_feature_name(entry)
        else:
            feature_name = entry

        try:
            if sys_path:
                sys.path.extend(sys_path)

            feature_module = importlib.import_module(feature_name)
        except:
            module = sys.modules.get(feature_name)
            if module:
                sys.modules.pop(feature_name)

            if sys_path:
                for path in sys_path:
                    while path in sys.path:
                        sys.path.remove(path)

            raise

        utils: Utils.FeatureUtils | None = getattr(feature_module, "utils", None)

        try:
            content: Utils.FeatureContent = getattr(feature_module, "content")

            if sys_path:
                content.sys_path = sys_path

        except AttributeError as attribute_error:
            raise Exception(
                f"[{feature_name}]: Feature content not found ({str(attribute_error)})"
            )

        return content, utils
