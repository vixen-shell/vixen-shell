from .references import AbsRootFeature, AbsRootContents
from .classes import State, StateItem, SocketHandler
from vx_types import (
    root_FeatureParams_dict,
    root_FrameParams_dict,
    root_LayerFrameParams_dict,
    root_MarginParams_dict,
)
from vx_logger import Logger
from vx_gtk import ContextMenu, show_message_dialog, show_confirm_dialog


def root_feature(feature_name: str = None) -> AbsRootFeature:
    from .references import get_root_feature_reference
    from vx_features import RootFeature
    from inspect import stack, getmodule

    package_name = getmodule(stack()[1].frame).__package__

    if not package_name:
        raise PermissionError(
            f"The usage of the 'feature' function only "
            "applies in the context of a feature package"
        )

    if feature_name:
        from vx_features import FeatureUtils

        if not feature_name in FeatureUtils.get_root_feature_names():
            raise KeyError(f"Unable to found feature named '{feature_name}'")

    else:
        feature_name = package_name.split(".")[0]

    return get_root_feature_reference(RootFeature(feature_name))


def root_content(feature_name: str = None) -> AbsRootContents:
    from .references import get_root_contents_reference
    from vx_features import RootContents
    from inspect import stack, getmodule

    package_name = getmodule(stack()[1].frame).__package__

    if not package_name:
        raise PermissionError(
            f"The usage of the 'content' function only "
            "applies in the context of a feature package"
        )

    if feature_name:
        from vx_features import FeatureUtils

        if not feature_name in FeatureUtils.get_root_feature_names():
            raise KeyError(f"Unable to found feature named '{feature_name}'")

    else:
        feature_name = package_name.split(".")[0]

    return get_root_contents_reference(RootContents(feature_name))
