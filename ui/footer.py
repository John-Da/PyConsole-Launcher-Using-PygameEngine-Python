import pygame
from ui.components import draw_round_rect


class Footer:
    """
    Bottom status bar:
      LEFT   — [L] Change Category
      CENTRE — [A] Confirm  [X] Detail  [B] Back
      RIGHT  — [R] Change Category
    """

    HEIGHT = 36
    SIDE_PAD = 24
    BADGE_W = 22
    BADGE_H = 22
    BADGE_RADIUS = 4
    HINT_GAP = 8  # gap between badge and its label
    HINT_SPACING = 20  # gap between consecutive hint groups

    def __init__(self, font_badge, font_label, app_version: str):
        """
        font_badge  — small bold font for the letter inside the badge
        font_label  — font for hint labels and version text
        app_version — shown on the far right (kept for future use / overlay)
        """
        self.font_badge = font_badge
        self.font_label = font_label
        self.app_version = app_version
        self._W = 0

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def update_layout(self, W: int):
        self._W = W

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _hint_width(self, label: str) -> int:
        """Total pixel width of one [X] Label group."""
        label_surf = self.font_label.render(label, True, (0, 0, 0))
        return self.BADGE_W + self.HINT_GAP + label_surf.get_width()

    def _draw_hint(
        self,
        screen,
        theme: dict,
        x: int,
        cy: int,
        letter: str,
        label: str,
        badge_color=None,
        letter_color=None,
    ) -> int:
        """
        Draws [letter] label centred vertically on cy.
        Returns x right after the rendered group.
        """
        badge_color = badge_color or theme["accent"]
        letter_color = letter_color or theme["bg"]

        badge_rect = pygame.Rect(x, cy - self.BADGE_H // 2, self.BADGE_W, self.BADGE_H)
        draw_round_rect(screen, badge_color, badge_rect, self.BADGE_RADIUS)

        l_surf = self.font_badge.render(letter, True, letter_color)
        screen.blit(l_surf, l_surf.get_rect(center=badge_rect.center))

        lbl_surf = self.font_label.render(label, True, theme["text"])
        screen.blit(
            lbl_surf,
            (badge_rect.right + self.HINT_GAP, cy - lbl_surf.get_height() // 2),
        )

        return badge_rect.right + self.HINT_GAP + lbl_surf.get_width()

    def _group_width(self, hints: list[tuple[str, str]]) -> int:
        """Total width of a list of (letter, label) hints with spacing between them."""
        total = 0
        for i, (letter, label) in enumerate(hints):
            total += self._hint_width(label)
            if i < len(hints) - 1:
                total += self.HINT_SPACING
        return total

    # ------------------------------------------------------------------
    # Public draw
    # ------------------------------------------------------------------

    def draw(self, screen, theme: dict):
        W = self._W or screen.get_width()
        H = screen.get_height()
        y0 = H - self.HEIGHT
        cy = y0 + self.HEIGHT // 2  # vertical centre of bar

        # Background
        pygame.draw.rect(screen, theme["header"], (0, y0, W, self.HEIGHT))
        pygame.draw.rect(screen, theme["accent"], (0, y0, W, 1))  # top separator

        # ------------------------------------------------------------------
        # LEFT — [L] Change Category
        # ------------------------------------------------------------------
        self._draw_hint(screen, theme, self.SIDE_PAD, cy, "L", "Change Category")

        # ------------------------------------------------------------------
        # RIGHT — [R] Change Category  (right-aligned)
        # ------------------------------------------------------------------
        r_w = self._hint_width("Change Category")
        self._draw_hint(
            screen, theme, W - self.SIDE_PAD - r_w, cy, "R", "Change Category"
        )

        # ------------------------------------------------------------------
        # CENTRE — [A] Confirm  [X] Detail  [B] Back
        # ------------------------------------------------------------------
        centre_hints = [("A", "Confirm"), ("X", "Detail"), ("B", "Back")]
        total_centre_w = self._group_width(centre_hints)
        x = W // 2 - total_centre_w // 2

        for i, (letter, label) in enumerate(centre_hints):
            x = self._draw_hint(screen, theme, x, cy, letter, label)
            if i < len(centre_hints) - 1:
                x += self.HINT_SPACING
