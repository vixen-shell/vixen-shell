import psutil


class SystemMetrics:
    @staticmethod
    def cpu_usage(percpu: bool = False) -> float | list[float]:
        return psutil.cpu_percent(percpu=percpu)

    @staticmethod
    def ram_usage() -> float:
        return psutil.virtual_memory().percent
