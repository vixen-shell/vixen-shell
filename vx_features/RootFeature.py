from vx_root.references.AbsLocales import AbsLocales, get_locales_reference
from vx_root.references.AbsFrames import AbsFrames
from vx_root.references.AbsParams import AbsParams
from vx_types import root_FeatureParams_dict
from .utils import FeatureUtils


class RootFeature:
    _instances = {}

    @classmethod
    def del_instance(cls, entry: str):
        feature_name = FeatureUtils.feature_name_from(entry)

        if feature_name in cls._instances:
            del cls._instances[feature_name]

    def __new__(cls, entry: str):
        feature_name = FeatureUtils.feature_name_from(entry)

        if feature_name not in cls._instances:
            cls._instances[feature_name] = super().__new__(cls)

        return cls._instances[feature_name]

    def __init__(self, entry: str) -> None:
        if not hasattr(self, "name"):
            self.name: str = FeatureUtils.feature_name_from(entry)
            self.root_params: root_FeatureParams_dict | None = None

            self.locales: AbsLocales = get_locales_reference(self.name)
            self.frames: AbsFrames = None
            self.params: AbsParams = None

    def init(self, value: root_FeatureParams_dict):
        self.root_params = value
