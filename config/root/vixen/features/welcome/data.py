import psutil
from . import feature


@feature.data
def cpu_usage(percpu: bool = False):
    return psutil.cpu_percent(percpu=percpu)


@feature.data
def ram_usage():
    return psutil.virtual_memory().percent
