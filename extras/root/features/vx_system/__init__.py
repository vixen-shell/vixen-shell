from vx_root import root_feature
from .infos import SystemInfos, SystemMetrics
from .tasks import System

root_feature().init(
    {
        "title": "System Module",
        "autostart": True,
        "frames": "disable",
    }
)
