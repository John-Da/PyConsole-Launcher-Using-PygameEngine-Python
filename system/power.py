class PowerManager:
    def __init__(self):
        self.battery_level = 100
        self.is_charging = False

    def update(self):
        # replace with real voltage read
        self.battery_level -= 0.01