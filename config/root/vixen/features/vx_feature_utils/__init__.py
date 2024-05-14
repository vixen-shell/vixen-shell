import importlib, os, sys
from .FeatureContent import FeatureContent, define_feature
from .parameters import (
    LevelKeys,
    AnchorEdgeKeys,
    AlignmentKeys,
    MarginParams,
    LayerFrameParams,
    FrameParams,
    FeatureParams,
)


def get_feature_names():
    from .utils import ROOT_PARAMS_DIRECTORY

    feature_names: list[str] = []

    for item in os.listdir(ROOT_PARAMS_DIRECTORY):
        path = f"{ROOT_PARAMS_DIRECTORY}/{item}"

        if os.path.isdir(path):
            feature_names.append(item)

    feature_names.remove("vx_feature_utils")
    return feature_names


def get_feature_content(entry: str) -> tuple[str, FeatureContent]:
    if os.path.exists(entry) and os.path.isdir(entry):
        from .utils import get_dev_feature_name

        sys.path.append(f"{entry}/config/root")

        feature_name = get_dev_feature_name(entry)
        feature_content: FeatureContent = importlib.import_module(feature_name).feature
        feature_content.dev_user_params_filepath = (
            f"{entry}/config/user/{feature_name}.json"
        )

        return feature_name, feature_content

    return entry, importlib.import_module(entry).feature
