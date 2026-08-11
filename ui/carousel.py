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
        font_meta  — used for the index/total counter above the carousel
        """
        self.font_title = font_title
        self.font_meta = font_meta
        self.selected = 0
        self._scroll_offset = 0.0  # current animated offset (in "slots")
        self._target_offset = 0.0  # target offset the animation lerps toward

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def move_left(self, num_items: int):
        if num_items == 0:
            return
        self.selected = (self.selected - 1) % num_items
        # Step the target by exactly -1 rather than snapping to the wrapped
        # index directly. Wrapping self.selected with % (e.g. 0 -> num_items-1)
        # would otherwise make the animation lerp across the ENTIRE list
        # instead of taking one short step backward.
        self._target_offset -= 1.0
        self._normalize_offsets(num_items)

    def move_right(self, num_items: int):
        if num_items == 0:
            return
        self.selected = (self.selected + 1) % num_items
        self._target_offset += 1.0
        self._normalize_offsets(num_items)

    def set_selected(self, index: int, num_items: int):
        """Jump directly to a given index (e.g. after a filter changes the list)."""
        if num_items == 0:
            self.selected = 0
            self._scroll_offset = 0.0
            self._target_offset = 0.0
            return
        self.selected = max(0, min(index, num_items - 1))
        self._scroll_offset = float(self.selected)
        self._target_offset = float(self.selected)

    def get_selected_game(self, games: list[dict]) -> dict | None:
        if not games:
            return None
        return games[self.selected]

    def _normalize_offsets(self, num_items: int):
        """
        Keep _scroll_offset/_target_offset from drifting to large magnitudes
        after many LEFT/RIGHT presses over a long session.

        This is now pure float hygiene, not a correctness requirement: the
        wraparound math in draw() uses true modulo, so it produces the right
        on-screen result no matter how large the offsets get. This just
        keeps the numbers small so they don't lose float precision over a
        very long play session.

        Safe to run any time (not just when idle): shifting both
        _scroll_offset and _target_offset by the same multiple of num_items
        doesn't change their difference (the animation delta), so it can't
        disturb an in-progress lerp.
        """
        if num_items == 0:
            return
        shift = round(self._scroll_offset / num_items) * num_items
        if shift:
            self._target_offset -= shift
            self._scroll_offset -= shift

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

    @staticmethod
    def _shortest_signed_distance(
        i: int, scroll_offset: float, num_items: int
    ) -> float:
        """
        Shortest signed distance from `scroll_offset` to slot `i` on a
        circular list of `num_items` slots.
        Uses round-to-nearest-multiple-of-num_items rather than a
        modulo + fixed-offset fold. That distinction only shows up for
        even-sized lists: with a "(raw_dist + half) % num_items - half"
        fold, an item exactly num_items/2 away always resolves to the
        SAME side (-half), no matter which direction you navigated to
        reach it. With exactly 2 items that pinned the "other" item to
        one fixed side permanently instead of letting it slide to
        whichever side it's actually animating from/to. Rounding instead
        breaks the tie using the sign of the raw distance, so it stays
        correct (and continuous through the lerp) in both directions.
        Also still robust to scroll_offset having drifted arbitrarily far
        from [0, num_items), same as the old modulo approach was.
        """
        raw_dist = i - scroll_offset
        if num_items <= 0:
            return raw_dist
        raw_dist -= num_items * round(raw_dist / num_items)
        return raw_dist

    def draw(self, screen, theme: dict, games: list[dict], rect: pygame.Rect):
        """
        Draws the carousel within `rect` (the area below the navbar / above
        the footer). Thumbnails are vertically centered in `rect`; the title
        is drawn below the centered thumbnail. An index/total counter
        (e.g. "5 / 16") is drawn above the thumbnails.
        """
        if not games:
            empty = self.font_title.render("No games found", True, theme["text"])
            screen.blit(empty, empty.get_rect(center=rect.center))
            return

        cx = rect.centerx
        cy = rect.centery - 20  # nudge up slightly to leave room for title below
        num_items = len(games)

        # ------------------------------------------------------------------
        # Index / total counter (e.g. "5 / 16") — shown above the carousel
        # ------------------------------------------------------------------
        counter_text = f"{self.selected + 1} / {num_items}"
        counter_color = theme.get("text_secondary", theme["text"])
        counter_font = pygame.font.SysFont("arial", 14, bold=True)
        counter_surf = counter_font.render(counter_text, True, counter_color)
        counter_y = rect.top + 20
        screen.blit(counter_surf, counter_surf.get_rect(centerx=cx, y=counter_y))

        for i, game in enumerate(games):
            # Shortest signed distance on a circular list (so wrap-around
            # looks continuous even if _scroll_offset has drifted far
            # outside [0, num_items) between normalization passes).
            raw_dist = self._shortest_signed_distance(i, self._scroll_offset, num_items)

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
