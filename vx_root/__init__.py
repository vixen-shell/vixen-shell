def feature(feature_name: str = None):
    from vx_features import RootFeature

    if feature_name:
        return RootFeature(feature_name)
    else:
        from inspect import stack, getmodule

        package_name = getmodule(stack()[1][0]).__package__

        if package_name:
            return RootFeature(package_name.split(".")[0])


def utils(feature_name: str = None):
    from vx_features import RootUtils

    if feature_name:
        return RootUtils(feature_name)
    else:
        from inspect import stack, getmodule

        package_name = getmodule(stack()[1][0]).__package__

        if package_name:
            return RootUtils(package_name.split(".")[0])
