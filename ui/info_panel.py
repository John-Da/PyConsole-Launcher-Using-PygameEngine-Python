import pygame
from ui.components import draw_round_rect


class InfoPanel:
    """
    Bottom-sheet style info panel showing metadata for the currently
    selected game (triggered by the Y / "Detail" button).

    Slides up from the footer when opened, slides back down when closed.
    """

    MAX_HEIGHT_RATIO = (
        0.55  # how much of the screen height the sheet covers when fully open
    )
    SLIDE_SPEED = 0.20  # lerp factor (0-1) for open/close animation
    CORNER_RADIUS = 20
    PADDING = 28
    ICON_SIZE = 96
    LINE_GAP = 6

    def __init__(self, font_title, font_label, font_body):
        """
        font_title — game name (large)
        font_label — field labels ("Author", "Version", etc) — typically bold/small
        font_body  — field values and description text
        """
        self.font_title = font_title
        self.font_label = font_label
        self.font_body = font_body

        self.is_open = False
        self._progress = 0.0  # 0 = fully closed, 1 = fully open
        self._game = None

    # ------------------------------------------------------------------
    # State control
    # ------------------------------------------------------------------

    def open(self, game: dict):
        """Open the panel for the given game dict."""
        self._game = game
        self.is_open = True

    def close(self):
        """Begin closing the panel (animates down, then is_open stays False)."""
        self.is_open = False

    def toggle(self, game: dict):
        """Toggle: open with `game` if closed, close if already open for any game."""
        if self.is_open:
            self.close()
        else:
            self.open(game)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt: float):
        target = 1.0 if self.is_open else 0.0
        diff = target - self._progress
        if abs(diff) < 0.002:
            self._progress = target
        else:
            self._progress += diff * self.SLIDE_SPEED

    def is_visible(self) -> bool:
        """True while the panel is open or still animating closed."""
        return self._progress > 0.001

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    def _draw_field(self, screen, theme, x, y, label, value, max_width):
        """Draw a 'LABEL  value' line, returns the y position after this line."""
        label_surf = self.font_label.render(label.upper(), True, theme["accent"])
        screen.blit(label_surf, (x, y))

        value_x = x + label_surf.get_width() + 10
        value_surf = self.font_body.render(str(value), True, theme["text"])
        screen.blit(value_surf, (value_x, y))

        return y + max(label_surf.get_height(), value_surf.get_height()) + self.LINE_GAP

    def _wrap_text(self, text: str, font, max_width: int) -> list[str]:
        """Simple word-wrap: returns a list of lines that fit within max_width."""
        words = text.split()
        lines = []
        current = ""

        for word in words:
            test = f"{current} {word}".strip()
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word

        if current:
            lines.append(current)

        return lines

    # ------------------------------------------------------------------
    # Main draw
    # ------------------------------------------------------------------

    def draw(self, screen, theme: dict, footer_height: int):
        """
        Draws the bottom sheet. `footer_height` is the height of the Footer
        bar — the sheet slides up from just above it.
        """
        if not self.is_visible() or self._game is None:
            return

        W, H = screen.get_size()
        sheet_h = int(H * self.MAX_HEIGHT_RATIO)

        # Slide animation: panel top moves from (H - footer_height) [closed]
        # up to (H - footer_height - sheet_h) [open]
        closed_y = H - footer_height
        open_y = H - footer_height - sheet_h
        current_y = int(closed_y + (open_y - closed_y) * self._progress)

        sheet_rect = pygame.Rect(0, current_y, W, sheet_h + footer_height + 20)

        # --- Background sheet ---
        sheet_surf = pygame.Surface(
            (sheet_rect.width, sheet_rect.height), pygame.SRCALPHA
        )
        draw_round_rect(
            sheet_surf,
            theme["header"],
            pygame.Rect(0, 0, sheet_rect.width, sheet_h),
            self.CORNER_RADIUS,
        )
        # Fill the remainder (so it seamlessly covers the footer area while open)
        pygame.draw.rect(
            sheet_surf,
            theme["header"],
            (
                0,
                self.CORNER_RADIUS,
                sheet_rect.width,
                sheet_rect.height - self.CORNER_RADIUS,
            ),
        )

        screen.blit(sheet_surf, sheet_rect.topleft)

        # --- Drag handle ---
        handle_w, handle_h = 50, 5
        handle_rect = pygame.Rect(0, 0, handle_w, handle_h)
        handle_rect.centerx = W // 2
        handle_rect.y = sheet_rect.y + 12
        draw_round_rect(screen, theme["accent"], handle_rect, 3)

        # --- Content layout ---
        content_x = self.PADDING
        content_y = sheet_rect.y + 28
        content_w = W - self.PADDING * 2

        game = self._game

        # Icon (left column)
        icon = game.get("icon")
        if icon:
            icon_surf = pygame.transform.smoothscale(
                icon, (self.ICON_SIZE, self.ICON_SIZE)
            )
            icon_rect = pygame.Rect(
                content_x, content_y, self.ICON_SIZE, self.ICON_SIZE
            )
            draw_round_rect(screen, theme["bg"], icon_rect, 12)
            screen.blit(icon_surf, icon_rect.topleft)
            text_x = icon_rect.right + 24
        else:
            text_x = content_x

        text_w = W - text_x - self.PADDING

        # Title
        title_surf = self.font_title.render(
            game.get("name", "Unknown"), True, theme["text"]
        )
        screen.blit(title_surf, (text_x, content_y))

        # Genre badge (if present) — drawn to the right of the title
        genre = game.get("genre")
        if genre:
            genre_surf = self.font_label.render(genre.upper(), True, theme["bg"])
            badge_w = genre_surf.get_width() + 20
            badge_h = genre_surf.get_height() + 8
            badge_rect = pygame.Rect(
                text_x + title_surf.get_width() + 14, content_y + 4, badge_w, badge_h
            )
            draw_round_rect(screen, theme["accent"], badge_rect, badge_h // 2)
            screen.blit(genre_surf, genre_surf.get_rect(center=badge_rect.center))

        field_y = content_y + title_surf.get_height() + 14

        # Meta fields row: Author / Version / Size / Entry
        field_y = self._draw_field(
            screen,
            theme,
            text_x,
            field_y,
            "Author",
            game.get("author", "Unknown"),
            text_w,
        )
        field_y = self._draw_field(
            screen,
            theme,
            text_x,
            field_y,
            "Version",
            game.get("version", "1.0"),
            text_w,
        )
        field_y = self._draw_field(
            screen, theme, text_x, field_y, "Size", game.get("size", "—"), text_w
        )
        field_y = self._draw_field(
            screen,
            theme,
            text_x,
            field_y,
            "Entry",
            game.get("entry", "main.py"),
            text_w,
        )

        field_y += 8

        # Description (word-wrapped)
        description = game.get("description")
        if description:
            desc_label = self.font_label.render("DESCRIPTION", True, theme["accent"])
            screen.blit(desc_label, (text_x, field_y))
            field_y += desc_label.get_height() + 4

            for line in self._wrap_text(description, self.font_body, text_w):
                line_surf = self.font_body.render(line, True, theme["text"])
                screen.blit(line_surf, (text_x, field_y))
                field_y += line_surf.get_height() + 2
