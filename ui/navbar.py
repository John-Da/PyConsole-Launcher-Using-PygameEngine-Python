import pygame
import time

try:
    import psutil

    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False

from ui.logo import AnimatedLogo

TAB_GAMES = "games"
TAB_STORE = "store"
TAB_SETTINGS = "settings"
TABS = [TAB_GAMES, TAB_STORE, TAB_SETTINGS]
TAB_LABELS = {TAB_GAMES: "Games", TAB_STORE: "Store", TAB_SETTINGS: "Settings"}

_WIFI_ICONS = {
    0: "\ue648",
    1: "\ue0c0",
    2: "\ue0c1",
    3: "\ue0c2",
    4: "\ue63e",
}


class NavBar:
    HEIGHT = 70
    LOGO_MAX_H = 24
    TAB_W = 110
    TAB_H = 44
    ACCENT_BAR_H = 3
    SIDE_PAD = 24
    STATUS_GAP = 16
    ICON_SIZE = 22

    def __init__(
        self,
        font_tab,
        font_status,
        font_icon,
        logo_path: str | None = None,
        frame_duration: float = 0.1,
    ):
        self.font_tab = font_tab
        self.font_status = font_status
        self.font_icon = font_icon

        self.logo = AnimatedLogo(logo_path, self.LOGO_MAX_H, frame_duration)

        self.tab_rects: dict[str, pygame.Rect] = {}
        self._W = 0

        self._last_status_update = 0.0
        self._battery_pct = None
        self._battery_charging = False
        self._wifi_strength = None
        self._clock_str = ""

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def update_layout(self, W: int):
        self._W = W
        cx = W // 2
        start_x = cx - (len(TABS) * self.TAB_W) // 2
        for i, tab in enumerate(TABS):
            self.tab_rects[tab] = pygame.Rect(
                start_x + i * self.TAB_W,
                (self.HEIGHT - self.TAB_H) // 2,
                self.TAB_W,
                self.TAB_H,
            )

    # ------------------------------------------------------------------
    # Status polling
    # ------------------------------------------------------------------
    def _refresh_status(self):
        now = time.time()
        if now - self._last_status_update < 1.0:
            return
        self._last_status_update = now

        self._clock_str = time.strftime("%H:%M")

        if _HAS_PSUTIL:
            try:
                b = psutil.sensors_battery()

                if b is not None:
                    self._battery_pct = int(b.percent)
                    self._battery_charging = b.power_plugged
                else:
                    self._battery_pct = None
                    self._battery_charging = False

            except Exception:
                self._battery_pct = None
                self._battery_charging = False

            try:
                stats = psutil.net_if_stats()

                wifi_names = (
                    "Wi-Fi",
                    "WLAN",
                    "wlan0",
                    "wlan1",
                    "en0",
                    "en1",
                )

                wifi_up = False

                for name, stat in stats.items():
                    lower_name = name.lower()

                    if (
                        lower_name.startswith("wl")
                        or name in wifi_names
                        or "wifi" in lower_name
                        or "wireless" in lower_name
                    ):
                        if stat.isup:
                            wifi_up = True
                            break

                self._wifi_strength = 4 if wifi_up else 0

            except Exception:
                self._wifi_strength = None

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def get_hover(self, m_pos) -> str | None:
        for tab, rect in self.tab_rects.items():
            if rect.collidepoint(m_pos):
                return f"tab:{tab}"
        return None

    def handle_click(self, m_pos) -> dict:
        for tab, rect in self.tab_rects.items():
            if rect.collidepoint(m_pos):
                return {"tab": tab}
        return {}

    # ------------------------------------------------------------------
    # Drawing — battery + wifi
    # ------------------------------------------------------------------

    def _draw_battery(self, screen, color, cx: int, cy: int, pct, charging):
        bw, bh = 22, 12
        tip_w, tip_h = 3, 6
        x = cx - bw // 2
        y = cy - bh // 2

        pygame.draw.rect(screen, color, (x, y, bw, bh), 2, border_radius=2)
        pygame.draw.rect(
            screen, color, (x + bw, cy - tip_h // 2, tip_w, tip_h), border_radius=1
        )

        if pct is not None:
            fill_w = max(1, int((bw - 4) * pct / 100))
            fill_color = (80, 200, 80) if pct > 20 else (220, 60, 60)
            if charging:
                fill_color = (80, 180, 255)
            pygame.draw.rect(
                screen, fill_color, (x + 2, y + 2, fill_w, bh - 4), border_radius=1
            )

        return bw + tip_w

    def _wifi_glyph(self) -> str:
        bars = self._wifi_strength
        if bars is None:
            return _WIFI_ICONS[0]
        return _WIFI_ICONS.get(max(0, min(4, bars)), _WIFI_ICONS[0])

    # ------------------------------------------------------------------
    # Main draw
    # ------------------------------------------------------------------

    def draw(self, screen, theme: dict, active_tab: str, m_pos, dt: float = 0.0):
        self._refresh_status()
        self.logo.update(dt)
        W = self._W or screen.get_width()

        pygame.draw.rect(screen, theme["header"], (0, 0, W, self.HEIGHT))
        pygame.draw.rect(screen, theme["accent"], (0, self.HEIGHT - 1, W, 1))

        cy = self.HEIGHT // 2

        # LEFT — Logo
        logo_surf = self.logo.current()
        if logo_surf:
            logo_y = (self.HEIGHT - logo_surf.get_height()) // 2
            screen.blit(logo_surf, (self.SIDE_PAD, logo_y))
        else:
            fb = self.font_tab.render("◈ APP", True, theme["accent"])
            screen.blit(fb, (self.SIDE_PAD, cy - fb.get_height() // 2))

        # CENTRE — Tabs
        hover_target = self.get_hover(m_pos)

        for tab in TABS:
            rect = self.tab_rects[tab]
            is_active = tab == active_tab
            is_hovered = hover_target == f"tab:{tab}"

            if is_hovered and not is_active:
                hover_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                hover_surf.fill((*theme["accent"][:3], 30))
                screen.blit(hover_surf, rect.topleft)

            color = theme["accent"] if is_active else theme["text"]
            txt = self.font_tab.render(TAB_LABELS[tab], True, color)
            screen.blit(txt, txt.get_rect(center=rect.center))

            if is_active:
                bar = pygame.Rect(
                    rect.x + 10,
                    rect.bottom - self.ACCENT_BAR_H - 2,
                    rect.width - 20,
                    self.ACCENT_BAR_H,
                )
                pygame.draw.rect(screen, theme["accent"], bar, border_radius=2)

        # RIGHT — Battery · WiFi · Clock
        icon_color = theme["text"]
        x = W - self.SIDE_PAD

        clk_surf = self.font_status.render(self._clock_str, True, icon_color)
        x -= clk_surf.get_width()
        screen.blit(clk_surf, (x, cy - clk_surf.get_height() // 2))
        x -= self.STATUS_GAP

        wifi_surf = self.font_icon.render(self._wifi_glyph(), True, icon_color)
        x -= wifi_surf.get_width()
        screen.blit(wifi_surf, wifi_surf.get_rect(midleft=(x, cy)))
        x -= self.STATUS_GAP

        if self._battery_pct is not None:
            BAT_TOTAL_W = 25
            x -= BAT_TOTAL_W
            bat_cx = x + BAT_TOTAL_W // 2

            self._draw_battery(
                screen,
                icon_color,
                bat_cx,
                cy,
                self._battery_pct,
                self._battery_charging,
            )
