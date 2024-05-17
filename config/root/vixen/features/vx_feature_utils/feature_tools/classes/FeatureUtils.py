from .AbstractLogger import AbstractLogger, get_logger_reference
from .AbstractFeature import AbstractFeature, get_feature_references
from .AbstractFeatures import AbstractFeatures, get_features_reference


class FeatureUtils:
    def init(self, logger, current_feature, features):
        self.logger: AbstractLogger = get_logger_reference(logger)
        self.current_feature: AbstractFeature = get_feature_references(current_feature)
        self.features: AbstractFeatures = get_features_reference(features)
