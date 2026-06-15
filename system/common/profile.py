PERFORMANCE_PRESETS = {
    "Battery Saver": {
        "fps": 30,
        "fan": "Low",
        "vsync": True,
    },
    "Balanced": {
        "fps": 60,
        "fan": "Balanced",
        "vsync": True,
    },
    "Performance": {
        "fps": 75,
        "fan": "High",
        "vsync": False,
    },
}

PROFILE_NAMES = list(PERFORMANCE_PRESETS.keys())
RENDER_QUALITY_OPTIONS = ["low", "medium", "high"]


class Profile:
    def __init__(self, name: str = "Balanced", render_quality: str = "medium"):
        self.name = name
        self.target_fps = 60
        self.fan_mode = "Balanced"
        self.vsync = True
        self.render_quality = render_quality

        self.set_profile(name)

    def set_profile(self, name: str):
        if name not in PERFORMANCE_PRESETS:
            raise ValueError(f"Unknown performance profile: {name!r}")

        preset = PERFORMANCE_PRESETS[name]
        self.name = name
        self.target_fps = preset["fps"]
        self.fan_mode = preset["fan"]
        self.vsync = preset["vsync"]
        # render_quality intentionally untouched — user preference, independent

    def cycle_profile(self):
        idx = PROFILE_NAMES.index(self.name)
        next_name = PROFILE_NAMES[(idx + 1) % len(PROFILE_NAMES)]
        self.set_profile(next_name)
        return self.name

    def cycle_render_quality(self):
        idx = RENDER_QUALITY_OPTIONS.index(self.render_quality)
        self.render_quality = RENDER_QUALITY_OPTIONS[
            (idx + 1) % len(RENDER_QUALITY_OPTIONS)
        ]
        return self.render_quality
