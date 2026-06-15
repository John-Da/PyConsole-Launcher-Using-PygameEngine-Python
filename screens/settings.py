import pygame
from ui.components import draw_round_rect, clear_rect_cache


class SettingsItem:
    def __init__(self, label, get_value, on_activate):
        self.label = label
        self.get_value = get_value
        self.on_activate = on_activate


class SettingsScreen:
    ROW_H = 44
    ROW_PAD_X = 20

    def __init__(
        self,
        font_main,
        font_meta,
        font_ui,
        system_manager,
        theme_manager,
        library_folder,
        vk,
        on_library_path_change=None,
        on_settings_changed=None,
    ):
        self.font_main = font_main
        self.font_meta = font_meta
        self.font_ui = font_ui
        self.system = system_manager
        self.theme_manager = theme_manager
        self.vk = vk
        self.library_folder = library_folder
        self.on_library_path_change = on_library_path_change
        self.on_settings_changed = on_settings_changed

        self.items = [
            SettingsItem(
                "Theme",
                lambda: self.theme_manager.current_name,
                self._cycle_theme,
            ),
            SettingsItem(
                "Performance Profile",
                lambda: self.system.profile.name,
                self._cycle_profile,
            ),
            SettingsItem(
                "Render Quality",
                lambda: self.system.profile.render_quality.capitalize(),
                self._cycle_render_quality,
            ),
            SettingsItem(
                "Game Library Path",
                lambda: self._truncate_path(self.library_folder),
                self._edit_library_path,
            ),
            SettingsItem(
                "Power Options",
                lambda: "",
                self._open_power_menu,
            ),
        ]

        self.selected_index = 0
        self._power_menu_requested = False
        self._editing_library_path = False

    # ------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------
    def _cycle_theme(self):
        self.theme_manager.next()
        clear_rect_cache()
        if self.on_settings_changed:
            self.on_settings_changed()

    def _cycle_profile(self):
        self.system.profile.cycle_profile()
        if self.on_settings_changed:
            self.on_settings_changed()

    def _cycle_render_quality(self):
        self.system.profile.cycle_render_quality()
        clear_rect_cache()
        if self.on_settings_changed:
            self.on_settings_changed()

    def _edit_library_path(self):
        self.vk.output = self.library_folder
        self.vk.active = True
        self._editing_library_path = True

    def _open_power_menu(self):
        self._power_menu_requested = True

    def _truncate_path(self, path, max_chars=28):
        if len(path) <= max_chars:
            return path
        return "…" + path[-(max_chars - 1) :]

    # ------------------------------------------------------------
    # Input
    # ------------------------------------------------------------
    def handle_input(self, actions):
        if actions["DOWN"]:
            self.selected_index = (self.selected_index + 1) % len(self.items)
        elif actions["UP"]:
            self.selected_index = (self.selected_index - 1) % len(self.items)
        elif actions["ACCEPT"]:
            self.items[self.selected_index].on_activate()

    def consume_power_menu_request(self) -> bool:
        if self._power_menu_requested:
            self._power_menu_requested = False
            return True
        return False

    def update(self, dt):
        pass

    def reset(self):
        self.selected_index = 0

    # ------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------
    def draw(self, screen, theme, content_rect, footer_h):
        quality = self.system.profile.render_quality

        ver_surf = self.font_meta.render(
            f"OS v{self.system.os_version}", True, theme["text"]
        )
        screen.blit(
            ver_surf,
            ver_surf.get_rect(centerx=content_rect.centerx, top=content_rect.top + 8),
        )

        y = content_rect.top + 50
        for i, item in enumerate(self.items):
            rect = pygame.Rect(
                content_rect.left + self.ROW_PAD_X,
                y,
                content_rect.width - self.ROW_PAD_X * 2,
                self.ROW_H,
            )

            is_selected = i == self.selected_index
            if is_selected:
                draw_round_rect(
                    screen, theme["accent"], rect, radius=8, quality=quality
                )

            label_color = theme["bg"] if is_selected else theme["text"]
            label_surf = self.font_ui.render(item.label, True, label_color)
            screen.blit(
                label_surf,
                (rect.x + 14, rect.centery - label_surf.get_height() // 2),
            )

            value_text = item.get_value()
            if value_text:
                value_surf = self.font_ui.render(value_text, True, label_color)
                screen.blit(
                    value_surf,
                    value_surf.get_rect(right=rect.right - 14, centery=rect.centery),
                )

            y += self.ROW_H + 8
