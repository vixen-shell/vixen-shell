from .Infos import SystemInfos
from .Metrics import SystemMetrics
from .Tasks import SystemTasks


class System(SystemTasks):
    Infos = SystemInfos
    Metrics = SystemMetrics
