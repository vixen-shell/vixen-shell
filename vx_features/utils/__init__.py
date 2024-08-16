import os


def is_dev_feature(entry: str):
    return (
        entry not in get_root_feature_names()
        and os.path.exists(entry)
        and os.path.isdir(entry)
    )


def feature_name_from(entry: str) -> str:
    def dev_module_name(dev_path: str) -> str:
        root_path = f"{dev_path}/root"
        root_items = [
            item
            for item in os.listdir(root_path)
            if os.path.isdir(f"{root_path}/{item}")
        ]

        if len(root_items) != 1:
            only = "only " if len(root_items) > 1 else ""
            raise Exception(
                f"Root folder should {only}contain one folder, cannot set feature package"
            )

        return root_items[0]

    return dev_module_name(entry) if is_dev_feature(entry) else entry


def get_root_feature_names():
    root_features_directory = "/usr/share/vixen/features"

    feature_names: list[str] = []

    for item in os.listdir(root_features_directory):
        path = f"{root_features_directory}/{item}"

        if os.path.isdir(path):
            feature_names.append(item)

    return feature_names
