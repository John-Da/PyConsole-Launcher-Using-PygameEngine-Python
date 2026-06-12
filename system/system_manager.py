from system.common.monitor import MonitorManager
from services.performance_manager import PerformanceManager
from system.common.power import Power
from system.common.profile import Profile


class SystemManager:
    def __init__(self):
        self.monitor = MonitorManager()
        self.power = Power()
        self.performance = PerformanceManager()
        self.options = Profile()

    def update(self):
        self.monitor.update()
        self.performance.apply_profile()