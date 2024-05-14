from .parameters import RootFeatureParamsDict, FeatureParams
from .utils import USER_PARAMS_DIRECTORY


class FeatureContent:
    def __init__(self, package_name: str, root_params_dict: RootFeatureParamsDict):
        self.feature_name = package_name
        self.root_params_dict = root_params_dict
        self.dev_user_params_filepath = None

        self.data_handlers = {}
        self.action_handlers = {}
        self.websocket_handlers = {}

    def data(self, callback):
        self.data_handlers[callback.__name__] = callback
        return callback

    def action(self, callback):
        self.action_handlers[callback.__name__] = callback
        return callback

    def websocket(self, callback):
        self.websocket_handlers[callback.__name__] = callback
        return callback

    def get_params(self):
        return FeatureParams.create(
            root_params_dict=self.root_params_dict,
            user_params_filepath=(
                f"{USER_PARAMS_DIRECTORY}/{self.feature_name}.json"
                if not self.dev_user_params_filepath
                else self.dev_user_params_filepath
            ),
            dev_mode=bool(self.dev_user_params_filepath),
        )


def define_feature(root_params_dict: RootFeatureParamsDict):
    from inspect import stack, getmodule

    return FeatureContent(getmodule(stack()[1][0]).__package__, root_params_dict)
