from system.monitor import MonitorManager
from system.optimizer import OptimizerManager
from system.power import PowerManager
from system.profile import OptionManager


class SystemManager:
    def __init__(self):
        self.monitor = MonitorManager()
        self.power = PowerManager()
        self.performance = OptimizerManager()
        self.options = OptionManager()

    def update(self):
        self.monitor.update()
        self.performance.apply_profile()