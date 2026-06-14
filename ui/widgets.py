import pygame


class Widgets:
    def __init__(self, font_title, font_button, font_message):
        self.font_title = font_title
        self.font_button = font_button
        self.font_message = font_message

        # Power menu state
        self.power_menu_open = False
        self.power_options = ["Sleep", "Restart", "Shutdown"]
        self.power_selected = 0

        # Notification/dialog state
        self.notification = None  # dict: {message, type, on_confirm, on_cancel}

    # ------------------------------------------------------------------
    # Power Menu
    # ------------------------------------------------------------------

    def open_power_menu(self):
        self.power_menu_open = True
        self.power_selected = 0

    def close_power_menu(self):
        self.power_menu_open = False

    def handle_power_input(self, actions):
        if not self.power_menu_open:
            return None

        if actions["LEFT"]:
            self.power_selected = (self.power_selected - 1) % len(self.power_options)
        if actions["RIGHT"]:
            self.power_selected = (self.power_selected + 1) % len(self.power_options)
        if actions["BACK"]:
            self.close_power_menu()
            return None
        if actions["ACCEPT"]:
            choice = self.power_options[self.power_selected]
            self.close_power_menu()
            return choice  # "Sleep" / "Restart" / "Shutdown"

        return None

    def draw_power_menu(self, screen, theme):
        if not self.power_menu_open:
            return

        W, H = screen.get_size()
        overlay = self._blur_overlay(screen)
        screen.blit(overlay, (0, 0))

        box_w, box_h = 360, 160
        box = pygame.Rect((W - box_w) // 2, (H - box_h) // 2, box_w, box_h)
        pygame.draw.rect(screen, theme["panel"], box, border_radius=12)
        pygame.draw.rect(screen, theme["border"], box, width=2, border_radius=12)

        title = self.font_title.render("Power Options", True, theme["text"])
        screen.blit(title, (box.centerx - title.get_width() // 2, box.y + 16))

        btn_w = 90
        spacing = 16
        total_w = btn_w * 3 + spacing * 2
        start_x = box.centerx - total_w // 2
        y = box.y + 80

        for i, label in enumerate(self.power_options):
            rect = pygame.Rect(start_x + i * (btn_w + spacing), y, btn_w, 40)
            selected = i == self.power_selected
            color = theme["accent"] if selected else theme["bg"]
            pygame.draw.rect(screen, color, rect, border_radius=8)
            text = self.font_button.render(label, True, theme["text"])
            screen.blit(text, text.get_rect(center=rect.center))

    # ------------------------------------------------------------------
    # Notifications / Dialogs
    # ------------------------------------------------------------------

    def show_notification(self, message, kind="info", on_confirm=None, on_cancel=None):
        """
        kind: "info" (OK only), "confirm" (Cancel/Confirm), "error" (OK only)
        """
        self.notification = {
            "message": message,
            "kind": kind,
            "on_confirm": on_confirm,
            "on_cancel": on_cancel,
            "selected": 0,  # 0 = left button, 1 = right button
        }

    def close_notification(self):
        self.notification = None

    def handle_notification_input(self, actions):
        if not self.notification:
            return

        n = self.notification

        if n["kind"] == "confirm":
            if actions["LEFT"] or actions["RIGHT"]:
                n["selected"] = 1 - n["selected"]
            if actions["BACK"]:
                if n["on_cancel"]:
                    n["on_cancel"]()
                self.close_notification()
            if actions["ACCEPT"]:
                if n["selected"] == 1:
                    if n["on_confirm"]:
                        n["on_confirm"]()
                else:
                    if n["on_cancel"]:
                        n["on_cancel"]()
                self.close_notification()
        else:
            # info / error -> single OK button
            if actions["ACCEPT"] or actions["BACK"]:
                if n["on_confirm"]:
                    n["on_confirm"]()
                self.close_notification()

    def draw_notification(self, screen, theme):
        if not self.notification:
            return

        n = self.notification
        W, H = screen.get_size()

        overlay = self._blur_overlay(screen)
        screen.blit(overlay, (0, 0))

        box_w, box_h = 420, 160
        box = pygame.Rect((W - box_w) // 2, (H - box_h) // 2, box_w, box_h)
        pygame.draw.rect(screen, theme["header"], box, border_radius=12)
        pygame.draw.rect(screen, theme["btn"], box, width=2, border_radius=12)

        # Wrap message text simply
        msg_surf = self.font_message.render(n["message"], True, theme["text"])
        screen.blit(msg_surf, (box.centerx - msg_surf.get_width() // 2, box.y + 24))

        btn_w, btn_h = 110, 40
        y = box.bottom - 56

        if n["kind"] == "confirm":
            cancel_rect = pygame.Rect(box.centerx - btn_w - 10, y, btn_w, btn_h)
            confirm_rect = pygame.Rect(box.centerx + 10, y, btn_w, btn_h)

            cancel_color = theme["accent"] if n["selected"] == 0 else theme["bg"]
            confirm_color = theme["accent"] if n["selected"] == 1 else theme["bg"]

            pygame.draw.rect(screen, cancel_color, cancel_rect, border_radius=8)
            pygame.draw.rect(screen, confirm_color, confirm_rect, border_radius=8)

            cancel_text = self.font_button.render("Cancel", True, theme["text"])
            confirm_text = self.font_button.render("Confirm", True, theme["text"])

            screen.blit(cancel_text, cancel_text.get_rect(center=cancel_rect.center))
            screen.blit(confirm_text, confirm_text.get_rect(center=confirm_rect.center))
        else:
            ok_rect = pygame.Rect(box.centerx - btn_w // 2, y, btn_w, btn_h)
            pygame.draw.rect(screen, theme["accent"], ok_rect, border_radius=8)
            ok_text = self.font_button.render("OK", True, theme["text"])
            screen.blit(ok_text, ok_text.get_rect(center=ok_rect.center))

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _blur_overlay(self, screen):
        """
        Pygame has no native blur. Approximation: downscale + upscale
        the current frame to soften it, then darken with a translucent layer.
        """
        W, H = screen.get_size()
        small = pygame.transform.smoothscale(screen, (W // 8, H // 8))
        blurred = pygame.transform.smoothscale(small, (W, H))

        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 150))  # adjust alpha for darkness
        blurred.blit(dim, (0, 0))

        return blurred

    @property
    def is_modal_open(self):
        return self.power_menu_open or self.notification is not None
