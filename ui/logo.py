import os
import pygame


class AnimatedLogo:
    def __init__(self, path: str | None, max_height: int, frame_duration: float = 0.1):
        self.max_height = max_height
        self.frame_duration = max(frame_duration, 0.01)
        self.frames: list[pygame.Surface] = []
        self.frame_idx = 0
        self.elapsed = 0.0

        if path and os.path.exists(path):
            if os.path.isdir(path):
                self._load_folder(path)
            else:
                self._load_single(path)
        else:
            print(f"[AnimatedLogo] Logo path not found or None: {path!r}")

    def _scale(self, surf: pygame.Surface) -> pygame.Surface:
        scale = self.max_height / surf.get_height()
        new_w = int(surf.get_width() * scale)
        return pygame.transform.smoothscale(surf, (new_w, self.max_height))

    def _load_single(self, path: str):
        try:
            raw = pygame.image.load(path).convert_alpha()
            self.frames = [self._scale(raw)]
        except Exception:
            self.frames = []

    def _load_folder(self, folder: str):
        valid_ext = (".png", ".jpg", ".jpeg", ".bmp")
        try:
            filenames = sorted(
                f for f in os.listdir(folder) if f.lower().endswith(valid_ext)
            )
        except Exception:
            return

        for fname in filenames:
            fpath = os.path.join(folder, fname)
            try:
                raw = pygame.image.load(fpath).convert_alpha()
                self.frames.append(self._scale(raw))
            except Exception as e:
                print(f"[AnimatedLogo] Skipping frame '{fpath}': {e}")

    def update(self, dt: float):
        if len(self.frames) <= 1:
            return
        self.elapsed += dt
        while self.elapsed >= self.frame_duration:
            self.elapsed -= self.frame_duration
            self.frame_idx = (self.frame_idx + 1) % len(self.frames)

    def current(self) -> pygame.Surface | None:
        if not self.frames:
            return None
        return self.frames[self.frame_idx]

    def draw(self, screen, x, y, fallback_text=None, fontstyle=None, color=None):
        surf = self.current()
        if surf:
            screen.blit(surf, (x, y))
        elif fallback_text and fontstyle:
            fb = fontstyle.render(fallback_text, True, color)
            screen.blit(fb, (x, y))
