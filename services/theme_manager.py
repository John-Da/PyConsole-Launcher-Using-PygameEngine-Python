import os
import pygame
from themes.system_theme import THEMES_DATA


class Theme:
    """
    Wraps a single theme entry. Acts like a dict for color access
    (theme["bg"], theme["text"], etc.) so existing code keeps working,
    while also exposing draw_background() for art/video themes.
    """

    def __init__(self, data: dict, resource_path_fn=None):
        self.name = data["name"]
        self.type = data.get("type", "solid")
        self.colors = data["colors"]
        self._resource_path_fn = resource_path_fn

        self.background_surface = None
        self.frames = []
        self.frame_duration = data.get("frame_duration", 0.1)
        self._frame_timer = 0.0
        self._frame_index = 0

        if self.type == "image":
            self._load_image(data.get("background_path"))
        elif self.type == "video":
            self._load_frames(data.get("background_path"))

    # ------------------------------------------------------------
    # Dict-like color access: theme["bg"], theme.get("panel"), etc.
    # ------------------------------------------------------------
    def __getitem__(self, key):
        return self.colors[key]

    def get(self, key, default=None):
        return self.colors.get(key, default)

    # ------------------------------------------------------------
    # Asset loading
    # ------------------------------------------------------------
    def _resolve_path(self, path_parts):
        if not path_parts:
            return None
        if self._resource_path_fn:
            return self._resource_path_fn(*path_parts)
        return os.path.join(*path_parts)

    def _load_image(self, path_parts):
        path = self._resolve_path(path_parts)
        if path and os.path.exists(path):
            try:
                self.background_surface = pygame.image.load(path).convert()
            except Exception:
                self.background_surface = None

    def _load_frames(self, path_parts):
        folder = self._resolve_path(path_parts)
        if folder and os.path.isdir(folder):
            for fname in sorted(os.listdir(folder)):
                if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                    try:
                        frame = pygame.image.load(os.path.join(folder, fname)).convert()
                        self.frames.append(frame)
                    except Exception:
                        pass

    # ------------------------------------------------------------
    # Update / Draw
    # ------------------------------------------------------------
    def update(self, dt):
        if self.type == "video" and self.frames:
            self._frame_timer += dt
            if self._frame_timer >= self.frame_duration:
                self._frame_timer = 0.0
                self._frame_index = (self._frame_index + 1) % len(self.frames)

    def draw_background(self, screen):
        W, H = screen.get_size()

        if self.type == "solid" or (
            self.type == "image" and self.background_surface is None
        ):
            screen.fill(self.colors["bg"])

        elif self.type == "image" and self.background_surface:
            scaled = pygame.transform.smoothscale(self.background_surface, (W, H))
            screen.blit(scaled, (0, 0))

        elif self.type == "video" and self.frames:
            frame = self.frames[self._frame_index]
            scaled = pygame.transform.smoothscale(frame, (W, H))
            screen.blit(scaled, (0, 0))

        else:
            screen.fill(self.colors["bg"])


class ThemeManager:
    def __init__(self, resource_path_fn=None):
        self._resource_path_fn = resource_path_fn
        self.themes = [Theme(data, resource_path_fn) for data in THEMES_DATA]
        self.current_index = 0

    @property
    def current(self) -> Theme:
        return self.themes[self.current_index]

    def set_index(self, index: int):
        if 0 <= index < len(self.themes):
            self.current_index = index

    def next(self):
        self.current_index = (self.current_index + 1) % len(self.themes)

    def previous(self):
        self.current_index = (self.current_index - 1) % len(self.themes)

    def update(self, dt):
        self.current.update(dt)

    def names(self):
        return [t.name for t in self.themes]
    
    @property
    def current_name(self) -> str:
        return self.current.name
