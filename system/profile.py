
PERFORMANCE_PRESETS = {
    "Battery Saver": {
        "fps": 30,
        "fan": "Low",
        "vsync": True
    },
    "Balanced": {
        "fps": 60,
        "fan": "Balanced",
        "vsync": True
    },
    "Performance": {
        "fps": 75,
        "fan": "High",
        "vsync": False
    }
}

class OptionManager:
    def __init__(self):
        pass

    def set_profile(self, name):
        preset = PERFORMANCE_PRESETS[name]
        self.target_fps = preset["fps"]
        self.fan_mode = preset["fan"]
        self.vsync = preset["vsync"]