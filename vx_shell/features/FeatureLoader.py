import sys
from importlib import import_module
from vx_root.references.AbsFrames import get_frames_reference
from vx_root.references.AbsParams import get_params_reference
from vx_config import VxConfig
from vx_logger import Logger

from vx_features import (
    FeatureUtils,
    RootContents,
    RootFeature,
    ParamDataHandler,
    ParamData,
    ParamsValueError,
)


class FeatureLoader:
    _instances = {}

    @classmethod
    def del_instance(cls, feature_name: str):
        if feature_name in cls._instances:
            del cls._instances[feature_name]

    def __new__(cls, entry: str, *args, **kwargs):
        feature_name = FeatureUtils.feature_name_from(entry)

        if feature_name not in cls._instances:
            cls._instances[feature_name] = super().__new__(cls)

        return cls._instances[feature_name]

    def __init__(self, entry: str, tty_path: str = None):
        if not hasattr(self, "is_loaded"):
            self.tty_path = tty_path
            self.feature_name = FeatureUtils.feature_name_from(entry)
            self.is_dev_feature = FeatureUtils.is_dev_feature(entry)
            self.sys_path = FeatureUtils.sys_path_from(entry)
            self.user_params_filepath = FeatureUtils.user_params_file_from(entry)
            self.feature = None

            self.is_loaded = False

    def __load_tty(self):
        if self.tty_path:
            Logger.add_handler(self.tty_path, "WARNING", True)

    def __unload_tty(self):
        if self.tty_path:
            Logger.remove_handler(self.tty_path)

    def __load_module(self):
        sys.path.extend(self.sys_path)
        import_module(self.feature_name)

    def __unload_module(self):
        RootContents.del_instance(self.feature_name)
        RootFeature.del_instance(self.feature_name)

        for module_name in list(sys.modules):
            if module_name.startswith(self.feature_name):
                del sys.modules[module_name]

        for path in self.sys_path:
            while path in sys.path:
                sys.path.remove(path)

    def __load_feature_params(self):
        root_params = RootFeature(self.feature_name).root_params

        if not root_params:
            raise Exception(
                f"The root parameters of the feature '{self.feature_name}' have not been defined"
            )

        try:
            ParamDataHandler.add_param_data(
                feature_name=self.feature_name,
                param_data=ParamData(
                    root_params_dict=root_params,
                    user_params_filepath=self.user_params_filepath,
                    dev_mode=self.is_dev_feature,
                ),
            )

            VxConfig.update_state(
                feature_state=ParamDataHandler.get_value(f"{self.feature_name}.state"),
                save=False if self.is_dev_feature else True,
            )

        except ParamsValueError as param_error:
            raise Exception(f"[{self.feature_name}]: {str(param_error)}")

    def __unload_feature_params(self):
        if self.is_dev_feature:
            VxConfig.update_state(
                feature_state=ParamDataHandler.get_value(f"{self.feature_name}.state"),
                option="remove",
                save=False,
            )

        ParamDataHandler.remove_param_data(self.feature_name)

    def __load_feature(self):
        from .Feature import Feature

        self.feature = Feature(
            feature_name=self.feature_name,
            dev_mode=self.is_dev_feature,
        )

    def __unload_feature(self):
        self.feature = None

    def __init_feature_utils(self):
        if self.feature:
            root_feature = RootFeature(self.feature_name)

            root_feature.frames = get_frames_reference(self.feature)
            root_feature.params = get_params_reference(
                self.feature_name, ParamDataHandler
            )

    def load(self):
        if self.is_loaded:
            raise Exception(f"Feature '{self.feature_name}' already loaded")

        try:
            self.__load_tty()
            self.__load_module()
            self.__load_feature_params()
            self.__load_feature()
            self.__init_feature_utils()

        except Exception as exception:
            Logger.log_exception(exception)
            self.unload()
            raise exception

        self.is_loaded = True
        return self.feature_name, self.feature

    def unload(self):
        self.__unload_feature()
        self.__unload_feature_params()
        self.__unload_module()
        self.__unload_tty()

        self.is_loaded = False
