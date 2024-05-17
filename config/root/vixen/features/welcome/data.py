import psutil
from . import content


@content.add("data")
def cpu_usage(percpu: bool = False):
    return psutil.cpu_percent(percpu=percpu)


@content.add("data")
def ram_usage():
    return psutil.virtual_memory().percent
