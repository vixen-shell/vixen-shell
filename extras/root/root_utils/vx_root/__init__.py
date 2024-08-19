def feature():
    from vx_features import RootFeature
    from inspect import stack, getmodule

    package_name = getmodule(stack()[1][0]).__package__

    if not package_name:
        raise Exception("Unable to find valid feature package")

    return RootFeature(package_name.split(".")[0])


def utils():
    from vx_features import RootUtils
    from inspect import stack, getmodule

    package_name = getmodule(stack()[1][0]).__package__

    if not package_name:
        raise Exception("Unable to find valid feature package")

    return RootUtils(package_name.split(".")[0])
