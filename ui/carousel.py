import pygame
from ui.components import draw_round_rect


class Carousel:
    """
    PS Vita-style horizontal game carousel.

    - Center item is large and fully opaque.
    - Side items shrink and fade out the further they are from center.
    - Only the centered item shows its title (below the thumbnail).
    - Navigation: LEFT/RIGHT to move selection, ACCEPT to launch.
    """

    CENTER_SIZE = 220  # thumbnail size of the active/centered item
    SIDE_SIZE = 140  # thumbnail size of immediate neighbors
    FAR_SIZE = 90  # thumbnail size of items 2+ away from center
    ITEM_GAP = 40  # horizontal gap between item edges
    CORNER_RADIUS = 16

    MAX_VISIBLE_SIDE = 2  # how many items to show on each side of center

    SCROLL_SPEED = 0.18  # lerp factor for smooth scrolling (0-1)

    def __init__(self, font_title, font_meta):
        """
        font_title — font for the centered game's title
        font_meta  — (reserved for future use: author/version under title)
        """
        self.font_title = font_title
        self.font_meta = font_meta

        self.selected = 0
        self._scroll_offset = 0.0  # current animated offset (in "slots")
        self._target_offset = 0.0  # target offset = selected index

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def move_left(self, num_items: int):
        if num_items == 0:
            return
        self.selected = (self.selected - 1) % num_items
        self._target_offset = float(self.selected)

    def move_right(self, num_items: int):
        if num_items == 0:
            return
        self.selected = (self.selected + 1) % num_items
        self._target_offset = float(self.selected)

    def set_selected(self, index: int, num_items: int):
        """Jump directly to a given index (e.g. after a filter changes the list)."""
        if num_items == 0:
            self.selected = 0
            self._target_offset = 0.0
            return
        self.selected = max(0, min(index, num_items - 1))
        self._target_offset = float(self.selected)

    def get_selected_game(self, games: list[dict]) -> dict | None:
        if not games:
            return None
        return games[self.selected]

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt: float):
        """Smoothly interpolate scroll offset toward target each frame."""
        diff = self._target_offset - self._scroll_offset
        if abs(diff) < 0.001:
            self._scroll_offset = self._target_offset
        else:
            self._scroll_offset += diff * self.SCROLL_SPEED

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _size_and_alpha_for_distance(self, dist: float) -> tuple[int, int]:
        """
        Given the fractional distance from center (0 = centered,
        1 = one slot away, etc), return (size, alpha) for the thumbnail.
        """
        dist = abs(dist)

        if dist >= self.MAX_VISIBLE_SIDE + 1:
            return 0, 0

        # Interpolate size: center -> side -> far
        if dist <= 1:
            t = dist  # 0..1
            size = int(self.CENTER_SIZE + (self.SIDE_SIZE - self.CENTER_SIZE) * t)
        else:
            t = min(dist - 1, self.MAX_VISIBLE_SIDE - 1)
            denom = max(self.MAX_VISIBLE_SIDE - 1, 1)
            size = int(self.SIDE_SIZE + (self.FAR_SIZE - self.SIDE_SIZE) * (t / denom))

        # Fade out toward the edges
        alpha_t = min(dist / (self.MAX_VISIBLE_SIDE + 1), 1.0)
        alpha = int(255 * (1.0 - alpha_t * 0.85))  # never fully invisible until cutoff

        return max(size, 0), max(alpha, 0)

    def draw(self, screen, theme: dict, games: list[dict], rect: pygame.Rect):
        """
        Draws the carousel within `rect` (the area below the navbar / above
        the footer). Thumbnails are vertically centered in `rect`; the title
        is drawn below the centered thumbnail.
        """
        if not games:
            empty = self.font_title.render("No games found", True, theme["text"])
            screen.blit(empty, empty.get_rect(center=rect.center))
            return

        cx = rect.centerx
        cy = rect.centery - 20  # nudge up slightly to leave room for title below

        num_items = len(games)

        for i, game in enumerate(games):
            # Shortest signed distance on a circular list (so wrap-around looks continuous)
            raw_dist = i - self._scroll_offset
            if raw_dist > num_items / 2:
                raw_dist -= num_items
            elif raw_dist < -num_items / 2:
                raw_dist += num_items

            size, alpha = self._size_and_alpha_for_distance(raw_dist)
            if size <= 0 or alpha <= 0:
                continue

            x = cx + raw_dist * (self.CENTER_SIZE + self.ITEM_GAP)
            y = cy

            item_rect = pygame.Rect(0, 0, size, size)
            item_rect.center = (int(x), int(y))

            # Skip items fully off-screen
            if item_rect.right < rect.left - 50 or item_rect.left > rect.right + 50:
                continue

            is_center = abs(raw_dist) < 0.05

            # --- Thumbnail surface (with alpha) ---
            thumb_surf = pygame.Surface((size, size), pygame.SRCALPHA)

            # Background card
            card_color = (*theme["header"][:3], alpha)
            draw_round_rect(
                thumb_surf,
                card_color,
                pygame.Rect(0, 0, size, size),
                self.CORNER_RADIUS,
            )

            # Icon
            icon = game.get("icon")
            if icon:
                pad = max(8, int(size * 0.08))
                icon_size = size - pad * 2
                scaled_icon = pygame.transform.smoothscale(icon, (icon_size, icon_size))
                scaled_icon.set_alpha(alpha)
                thumb_surf.blit(scaled_icon, (pad, pad))

            # Accent border for the centered item
            if is_center:
                border_rect = pygame.Rect(0, 0, size, size)
                draw_round_rect(
                    thumb_surf, theme["accent"], border_rect, self.CORNER_RADIUS, 4
                )

            screen.blit(thumb_surf, item_rect.topleft)

        # ------------------------------------------------------------------
        # Title — only for the centered item
        # ------------------------------------------------------------------
        active_game = games[self.selected]
        title_surf = self.font_title.render(active_game["name"], True, theme["text"])
        title_y = cy + self.CENTER_SIZE // 2 + 20
        screen.blit(title_surf, title_surf.get_rect(centerx=cx, y=title_y))
