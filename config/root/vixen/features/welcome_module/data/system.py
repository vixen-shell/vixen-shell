import psutil


def cpu_usage(percpu: bool = False):
    return psutil.cpu_percent(percpu=percpu)


def ram_usage():
    return psutil.virtual_memory().percent
