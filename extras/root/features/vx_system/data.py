import os, psutil
from vx_root import content


@content().dispatch("data")
def user_name() -> str:
    return os.getlogin()


@content().dispatch("data")
def user_directory() -> str:
    return os.path.expanduser("~")


@content().dispatch("data")
def cpu_usage(percpu: bool = False) -> float | list[float]:
    return psutil.cpu_percent(percpu=percpu)


@content().dispatch("data")
def ram_usage() -> float:
    return psutil.virtual_memory().percent
