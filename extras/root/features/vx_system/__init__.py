from vx_root import root_feature
from .infos import SysInfos
from .files import SysFiles
from .tasks import SysTasks

root_feature().init(
    {
        "autostart": True,
        "frames": "disable",
        "state": "disable",
    }
)
