from vx_feature_utils import Utils

utils = Utils.define_feature_utils()
content = Utils.define_feature_content({"autostart": True})

from .hypr_events import HyprEventsListener


@content.on_startup
def on_startup():
    HyprEventsListener.start()


@content.on_shutdown
def on_shutdown():
    HyprEventsListener.stop()


from .events_socket import *
from .hypr_infos import *
