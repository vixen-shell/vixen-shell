from vx_features import ParamDataHandler


class FeatureFrameParams:
    def __init__(self, feature_name: str):
        self.__feature_name = feature_name
        self.__main_path = f"{feature_name}.frames"

    @property
    def frame_ids(self):
        return ParamDataHandler.get_frame_ids(self.__feature_name)

    def __call__(self, frame_id: str, path: str):
        return ParamDataHandler.get_value(f"{self.__main_path}.{frame_id}.{path}")
