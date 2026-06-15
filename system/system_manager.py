from system.common.monitor import Monitor
from system.common.power import Power
from system.common.profile import Profile


class SystemManager:
    def __init__(self, os_version="0.1.0"):
        self.monitor = Monitor()
        self.power = Power()
        self.profile = Profile("Balanced")
        self.os_version = os_version

    def update(self):
        self.monitor.update()
        self.power.update()
