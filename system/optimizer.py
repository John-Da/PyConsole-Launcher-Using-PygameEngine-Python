AVAILABLE_GPU = ['OpenGL', 'Vulkan']

class OptimizerManager:
    def __init__(self):
        self.render_backend = "OpenGL"
        self.target_fps = 60
        self.vsync = True
        self.performance_profile = "Balanced"

    def apply_profile(self):
        if self.performance_profile == "Low":
            self.target_fps = 30
        elif self.performance_profile == "Balanced":
            self.target_fps = 60
        elif self.performance_profile == "High":
            self.target_fps = 75