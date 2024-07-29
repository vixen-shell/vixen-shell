import os, psutil
from . import content


@content.add_handler("data")
def user():
    return os.getlogin()


@content.add_handler("data")
def user_home():
    return os.path.expanduser("~")


@content.add_handler("data")
def cpu_usage(percpu: bool = False):
    return psutil.cpu_percent(percpu=percpu)


@content.add_handler("data")
def ram_usage():
    return psutil.virtual_memory().percent
