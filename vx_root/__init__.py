from .references import RootFeatureReference
from .classes import SocketHandler


def feature() -> RootFeatureReference:
    from vx_features import RootFeature
    from inspect import stack, getmodule

    package_name = getmodule(stack()[1][0]).__package__

    if not package_name:
        raise Exception("Unable to find valid feature package")

    return RootFeature(package_name.split(".")[0])
