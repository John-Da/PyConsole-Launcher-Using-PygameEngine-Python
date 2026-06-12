class FanController:
    def __init__(self):
        self.mode = "Balanced"

    def apply_curve(self, temperature):
        if self.mode == "Low":
            speed = 30
        elif self.mode == "Normal":
            speed = 50
        elif self.mode == "Balanced":
            speed = 70 if temperature > 60 else 40
        elif self.mode == "High":
            speed = 100
        return speed