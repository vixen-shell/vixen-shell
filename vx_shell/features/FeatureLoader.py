import os, sys
from importlib import import_module
from vx_features import (
    FeatureUtils,
    RootFeature,
    ParamDataHandler,
    ParamData,
    ParamsValueError,
)

from vx_root.references.AbsFrames import get_frames_reference
from vx_root.references.AbsParams import get_params_reference
from vx_root.references.AbsLogger import get_logger_reference

from .Gtk_dialog import show_dialog_box
from ..logger import Logger

USER_PARAMS_DIRECTORY = f"{os.path.expanduser('~')}/.config/vixen/features"


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

            self.is_loaded = False

    def __load_module(self):
        sys.path.extend(self.sys_path)
        import_module(self.feature_name)

    def __unload_module(self):
        for module_name in list(sys.modules):
            if module_name.startswith(self.feature_name):
                del sys.modules[module_name]

        for path in self.sys_path:
            while path in sys.path:
                sys.path.remove(path)

    def __init_tty(self):
        if self.tty_path:
            Logger.add_handler(self.tty_path, "WARNING", True)

    def __init_feature_params(self):
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

        except ParamsValueError as param_error:
            raise Exception(f"[{self.feature_name}]: {str(param_error)}")

    def load(self):
        from .Feature import Feature

        if self.is_loaded:
            raise Exception(f"Feature '{self.feature_name}' already loaded")

        try:
            self.__init_tty()
            self.__load_module()
            self.__init_feature_params()

            root_feature = RootFeature(self.feature_name)

            feature = Feature(
                feature_name=self.feature_name,
                required_features=root_feature.required_features,
                shared_content=root_feature.shared_content,
                lifespan=root_feature.lifespan,
                dev_mode=self.is_dev_feature,
            )

            root_feature.frames = get_frames_reference(feature)
            root_feature.params = get_params_reference(
                self.feature_name, ParamDataHandler
            )
            root_feature.logger = get_logger_reference(Logger)
            root_feature.dialog = show_dialog_box

            self.is_loaded = True

            return self.feature_name, feature

        except Exception as exception:
            Logger.log(str(exception), "ERROR")
            show_dialog_box(str(exception), "WARNING")
            raise exception

    def unload(self):
        if not self.is_loaded:
            raise Exception(f"Feature '{self.feature_name}' is not loaded")

        try:
            RootFeature.del_instance(self.feature_name)
            ParamDataHandler.remove_param_data(self.feature_name)
            self.__unload_module()

            if self.tty_path:
                Logger.remove_handler(self.tty_path)

            self.is_loaded = False

        except Exception as exception:
            Logger.log(str(exception), "ERROR")
            raise exception
