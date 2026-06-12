import pygame

class Monitor:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.current_fps = 0
        self.frame_time = 0

    def tick(self, target_fps):
        self.frame_time = self.clock.tick(target_fps)
        self.current_fps = self.clock.get_fps()

    def update(self):
        self.current_fps = self.clock.get_fps()