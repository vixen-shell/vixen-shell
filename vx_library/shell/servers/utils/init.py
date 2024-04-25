import logging
from multiprocessing import Queue
from ...hypr_events import HyprEventsListener
from ...features import Features
from ...logger import Logger


def init_api_requirements():
    if not HyprEventsListener.check_hypr_socket():
        Logger.log("Hyprland socket not found", "WARNING")
        Logger.log("Sorry, Vixen Shell only starts with Hyprland")
        return False
    else:
        Logger.log("Hyprland socket found")

    if not Features.init():
        Logger.log("Sorry, unable to initialize features", "WARNING")
        return False
    else:
        Logger.log("Features initialization successful")

    return True


def init_front_logging(queue: Queue):
    class LogHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            queue.put({"level": record.levelname, "message": record.getMessage()})

    logger = logging.getLogger("gunicorn")
    logger.addHandler(LogHandler())
