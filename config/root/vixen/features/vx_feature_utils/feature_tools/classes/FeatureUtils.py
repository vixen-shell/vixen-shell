from .AbstractLogger import AbstractLogger, get_logger_reference
from .AbstractFeature import AbstractFeature, get_feature_references
from .AbstractFeatures import AbstractFeatures, get_features_reference


class FeatureUtils:
    def init(self, logger, current_feature, features):
        self.Logger: AbstractLogger = get_logger_reference(logger)
        self.CurrentFeature: AbstractFeature = get_feature_references(current_feature)
        self.Features: AbstractFeatures = get_features_reference(features)
