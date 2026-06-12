import pygame

from ui.components import draw_round_rect


class VirtualKeyboard:
    def __init__(self, fontstyle):
        self.fontstyle = fontstyle
        self.layout = [
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "Back"],
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L", "Enter"],
            ["Z", "X", "C", "V", "B", "N", "M", " ", "Done"]
        ]
        self.active = False
        self.output = ""
        self.focus_pos = [0, 0]  # [row, col]
        self.key_rects = {}  # Stores {(row, col): Rect} for touch detection

    def draw(self, surf, theme):
        # Dim the background
        overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surf.blit(overlay, (0, 0))

        key_w, key_h = 70, 70
        gutter = 10
        start_y = surf.get_height() // 2 - 50

        for r, row in enumerate(self.layout):
            # Center the row
            total_row_w = len(row) * (key_w + gutter)
            start_x = (surf.get_width() - total_row_w) // 2

            for c, key in enumerate(row):
                # Make specific keys wider
                current_w = key_w * 2 if key in ("Enter", "Done", "Back") else key_w
                rect = pygame.Rect(start_x + c * (key_w + gutter), start_y + r * (key_h + gutter), current_w, key_h)
                self.key_rects[(r, c)] = rect  # Store for touch logic

                # Determine Colors (Highlight if controller focus)
                is_focused = (self.focus_pos == [r, c])
                bg = theme["accent"] if is_focused else theme["header"]
                txt_col = theme["bg"] if is_focused else theme["text"]

                draw_round_rect(surf, bg, rect, 8)
                t_surf = self.fontstyle.render(key, True, txt_col)
                surf.blit(t_surf, t_surf.get_rect(center=rect.center))

    def handle_input(self, action, m_pos, is_click):
        selected_key = None

        # --- TOUCH / MOUSE LOGIC ---
        if is_click:
            for coords, rect in self.key_rects.items():
                if rect.collidepoint(m_pos):
                    selected_key = self.layout[coords[0]][coords[1]]
                    self.focus_pos = list(coords)  # Sync controller focus to touch
                    break

        # --- CONTROLLER / KEYBOARD LOGIC ---
        if action == "UP": self.focus_pos[0] = max(0, self.focus_pos[0] - 1)
        if action == "DOWN": self.focus_pos[0] = min(len(self.layout) - 1, self.focus_pos[0] + 1)
        if action == "LEFT": self.focus_pos[1] = max(0, self.focus_pos[1] - 1)
        if action == "RIGHT": self.focus_pos[1] = min(len(self.layout[self.focus_pos[0]]) - 1, self.focus_pos[1] + 1)

        # Snap column to valid index if row is shorter
        self.focus_pos[1] = min(self.focus_pos[1], len(self.layout[self.focus_pos[0]]) - 1)

        if action == "ACCEPT" and not is_click:  # Controller 'A' or Enter key
            selected_key = self.layout[self.focus_pos[0]][self.focus_pos[1]]

        # --- ACTION THE KEY ---
        if selected_key:
            if selected_key == "Back":
                self.output = self.output[:-1]
            elif selected_key in ("Enter", "Done"):
                self.active = False
            else:
                self.output += selected_key