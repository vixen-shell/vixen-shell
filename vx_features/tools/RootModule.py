import sys
from importlib import import_module
from glob import glob
from ..utils import feature_name_from, is_dev_feature


class RootModule:
    _instances = {}

    @classmethod
    def del_instance(cls, entry: str):
        feature_name = feature_name_from(entry)

        if feature_name in cls._instances:
            instance: RootModule = cls._instances[feature_name]

            for name in list(sys.modules):
                if name.startswith(instance.name):
                    del sys.modules[name]

            for path in instance.sys_path:
                while path in sys.path:
                    sys.path.remove(path)

            instance = None
            del cls._instances[feature_name]

    def __new__(cls, entry: str):
        feature_name = feature_name_from(entry)

        if feature_name not in cls._instances:
            cls._instances[feature_name] = super().__new__(cls)

        return cls._instances[feature_name]

    def __init__(self, entry: str):
        if not hasattr(self, "name"):
            self.name = feature_name_from(entry)
            self.dev_mode = is_dev_feature(entry)

            if self.dev_mode:
                self.sys_path = [f"{entry}/root"] + glob(
                    f"{entry}/.venv/lib/python*/site-packages"
                )
            else:
                self.sys_path = glob(f"/usr/share/vixen/{self.name}.libs")

            sys.path.extend(self.sys_path)
            import_module(self.name)
