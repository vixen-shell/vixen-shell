import os, psutil


class Data:
    @staticmethod
    def user_name() -> str:
        return os.getlogin()

    @staticmethod
    def user_directory() -> str:
        return os.path.expanduser("~")

    @staticmethod
    def cpu_usage(percpu: bool = False) -> float | list[float]:
        return psutil.cpu_percent(percpu=percpu)

    @staticmethod
    def ram_usage() -> float:
        return psutil.virtual_memory().percent
