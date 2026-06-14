import pygame
import os
import math
import time

try:
    import psutil

    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False

from ui.components import draw_round_rect

TAB_GAMES = "games"
TAB_STORE = "store"
TAB_SETTINGS = "settings"
TABS = [TAB_GAMES, TAB_STORE, TAB_SETTINGS]
TAB_LABELS = {TAB_GAMES: "Games", TAB_STORE: "Store", TAB_SETTINGS: "Settings"}


class NavBar:
    """
    Top navbar:
      LEFT   — app logo (png/svg)
      CENTRE — Games | Store | Settings tabs  (underline indicator)
      RIGHT  — Battery · WiFi · Clock
    """

    HEIGHT = 70
    LOGO_MAX_H = 24
    TAB_W = 110
    TAB_H = 44
    ACCENT_BAR_H = 3
    SIDE_PAD = 24
    STATUS_GAP = 14  # gap between status items
    STATUS_ICON_W = 24  # bounding box for drawn icons

    def __init__(
        self,
        font_tab,
        font_status,
        logo_path: str | None = None,
        frame_duration: float = 0.1,
    ):
        """
        font_tab       — font for tab labels
        font_status    — small font for clock text and battery %
        logo_path      — EITHER a path to a single static image (png/jpg),
                        OR a path to a folder containing numbered frame
                        images (frame_00.png, frame_01.png, ...).
                        None → text fallback.
        frame_duration — seconds per frame when logo_path is a folder
                        (ignored for single static images).
        """
        self.font_tab = font_tab
        self.font_status = font_status

        # Logo — supports a single static image OR a folder of numbered frames
        self._logo_frames: list[pygame.Surface] = []
        self._logo_frame_idx = 0
        self._logo_elapsed = 0.0
        self._logo_frame_duration = max(frame_duration, 0.01)

        if logo_path and os.path.exists(logo_path):
            if os.path.isdir(logo_path):
                self._load_frame_folder(logo_path)
            else:
                self._load_single_image(logo_path)
        else:
            print(f"[NavBar] Logo path not found or None: {logo_path!r}")

        self.tab_rects: dict[str, pygame.Rect] = {}
        self._W = 0

        # Status cache — refresh every second
        self._last_status_update = 0.0
        self._battery_pct = None  # 0–100 or None
        self._battery_charging = False
        self._wifi_strength = None  # 0–4 bars or None
        self._clock_str = ""

    # ------------------------------------------------------------------
    # Logo loading / animation
    # ------------------------------------------------------------------

    def _scale_to_logo_height(self, surf: pygame.Surface) -> pygame.Surface:
        scale = self.LOGO_MAX_H / surf.get_height()
        new_w = int(surf.get_width() * scale)
        return pygame.transform.smoothscale(surf, (new_w, self.LOGO_MAX_H))

    def _load_single_image(self, path: str):
        """Load one static image (png/jpg/etc) as a single-frame logo."""
        try:
            raw = pygame.image.load(path).convert_alpha()
            self._logo_frames = [self._scale_to_logo_height(raw)]
            print(f"[NavBar] Loaded static logo from '{path}'")
        except Exception as e:
            print(f"[NavBar] Failed to load logo image '{path}': {e}")
            self._logo_frames = []

    def _load_frame_folder(self, folder: str):
        """
        Load a folder of numbered frame images (frame_00.png, frame_01.png, ...)
        as an animation sequence. Files are sorted alphabetically/numerically
        by filename, so zero-pad your frame numbers (e.g. frame_00, frame_01,
        ... frame_10) for correct ordering.
        """
        valid_ext = (".png", ".jpg", ".jpeg", ".bmp")
        try:
            filenames = sorted(
                f for f in os.listdir(folder) if f.lower().endswith(valid_ext)
            )
        except Exception as e:
            print(f"[NavBar] Failed to read logo frame folder '{folder}': {e}")
            return

        if not filenames:
            print(f"[NavBar] No frame images found in '{folder}'")
            return

        for fname in filenames:
            fpath = os.path.join(folder, fname)
            try:
                raw = pygame.image.load(fpath).convert_alpha()
                self._logo_frames.append(self._scale_to_logo_height(raw))
            except Exception as e:
                print(f"[NavBar] Skipping frame '{fpath}': {e}")

        print(f"[NavBar] Loaded {len(self._logo_frames)} logo frames from '{folder}'")

    def _advance_logo_animation(self, dt: float):
        """Call once per frame with delta-time (seconds) to step the logo animation."""
        if len(self._logo_frames) <= 1:
            return

        self._logo_elapsed += dt
        while self._logo_elapsed >= self._logo_frame_duration:
            self._logo_elapsed -= self._logo_frame_duration
            self._logo_frame_idx = (self._logo_frame_idx + 1) % len(self._logo_frames)

    def _current_logo_surface(self) -> pygame.Surface | None:
        if not self._logo_frames:
            return None
        return self._logo_frames[self._logo_frame_idx]

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

        # Clock
        self._clock_str = time.strftime("%H:%M")

        # Battery (via psutil — works on Linux/RPi)
        if _HAS_PSUTIL:
            try:
                b = psutil.sensors_battery()
                if b:
                    self._battery_pct = int(b.percent)
                    self._battery_charging = b.power_plugged
            except Exception:
                self._battery_pct = None

        # WiFi strength — try psutil net_if_stats as a fallback signal
        # On RPi you can replace this with subprocess iwconfig parsing if needed
        if _HAS_PSUTIL:
            try:
                stats = psutil.net_if_stats()
                # Consider 'wlan0' up = connected (4 bars); refine with iwconfig if desired
                wlan = stats.get("wlan0") or stats.get("wlp2s0") or stats.get("wlo1")
                if wlan and wlan.isup:
                    self._wifi_strength = (
                        4  # connected; strength unknown without iwconfig
                    )
                else:
                    self._wifi_strength = 0
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
        """Returns {'tab': <name>} or {} ."""
        for tab, rect in self.tab_rects.items():
            if rect.collidepoint(m_pos):
                return {"tab": tab}
        return {}

    # ------------------------------------------------------------------
    # Drawing — status icons
    # ------------------------------------------------------------------

    def _draw_battery(
        self, screen, color, cx: int, cy: int, pct: int | None, charging: bool
    ):
        """Draw a small battery icon centred on (cx, cy). Returns icon right-edge x."""
        bw, bh = 22, 12
        tip_w, tip_h = 3, 6
        x = cx - bw // 2
        y = cy - bh // 2

        # Outer shell
        pygame.draw.rect(screen, color, (x, y, bw, bh), 2, border_radius=2)
        # Tip nub
        pygame.draw.rect(
            screen, color, (x + bw, cy - tip_h // 2, tip_w, tip_h), border_radius=1
        )

        # Fill bar
        if pct is not None:
            fill_w = max(1, int((bw - 4) * pct / 100))
            fill_color = (80, 200, 80) if pct > 20 else (220, 60, 60)
            if charging:
                fill_color = (80, 180, 255)
            pygame.draw.rect(
                screen, fill_color, (x + 2, y + 2, fill_w, bh - 4), border_radius=1
            )

        return x + bw + tip_w

    def _draw_wifi(self, screen, color, cx: int, cy: int, bars: int | None):
        """Draw a 4-arc WiFi icon. bars=0 draws an X. Returns icon right-edge x."""
        r_step = 5
        num_arcs = 4
        total_r = r_step * num_arcs
        x_left = cx - total_r

        if bars is None or bars == 0:
            # Draw ✕ to indicate no signal
            s = 7
            pygame.draw.line(screen, color, (cx - s, cy - s), (cx + s, cy + s), 2)
            pygame.draw.line(screen, color, (cx + s, cy - s), (cx - s, cy + s), 2)
            return cx + total_r

        for i in range(num_arcs):
            r = r_step * (i + 1)
            arc_color = color if (i < bars) else (*color[:3],)  # dim inactive arcs
            if i >= bars:
                dim = tuple(max(0, c - 80) for c in color[:3])
                arc_color = dim
            rect = pygame.Rect(cx - r, cy - r + r_step, r * 2, r * 2)
            pygame.draw.arc(
                screen, arc_color, rect, math.radians(30), math.radians(150), 2
            )

        return cx + total_r

    # ------------------------------------------------------------------
    # Main draw
    # ------------------------------------------------------------------

    def draw(self, screen, theme: dict, active_tab: str, m_pos, dt: float = 0.0):
        self._refresh_status()
        self._advance_logo_animation(dt)
        W = self._W or screen.get_width()

        # Background + separator
        pygame.draw.rect(screen, theme["header"], (0, 0, W, self.HEIGHT))
        pygame.draw.rect(screen, theme["accent"], (0, self.HEIGHT - 1, W, 1))

        cy = self.HEIGHT // 2  # vertical centre

        # ------------------------------------------------------------------
        # LEFT — Logo (static image or animated GIF frame)
        # ------------------------------------------------------------------
        logo_surf = self._current_logo_surface()
        if logo_surf:
            logo_y = (self.HEIGHT - logo_surf.get_height()) // 2
            screen.blit(logo_surf, (self.SIDE_PAD, logo_y))
        else:
            fb = self.font_tab.render("◈ APP", True, theme["accent"])
            screen.blit(fb, (self.SIDE_PAD, cy - fb.get_height() // 2))

        # ------------------------------------------------------------------
        # CENTRE — Tabs
        # ------------------------------------------------------------------
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

        # ------------------------------------------------------------------
        # RIGHT — Battery · WiFi · Clock
        # Laid out right-to-left then rendered left-to-right
        # ------------------------------------------------------------------
        icon_color = theme["text"]

        # 1. Clock (rightmost)
        clk_surf = self.font_status.render(self._clock_str, True, icon_color)
        clk_x = W - self.SIDE_PAD - clk_surf.get_width()
        clk_y = cy - clk_surf.get_height() // 2
        screen.blit(clk_surf, (clk_x, clk_y))

        # 2. WiFi icon (left of clock)
        wifi_cx = clk_x - self.STATUS_GAP - self.STATUS_ICON_W // 2
        self._draw_wifi(screen, icon_color, wifi_cx, cy + 4, self._wifi_strength)

        # 3. Battery icon (left of wifi)
        bat_right_x = wifi_cx - self.STATUS_ICON_W // 2 - self.STATUS_GAP
        bat_cx = bat_right_x - 13  # half of battery width (22/2 + tip)
        self._draw_battery(
            screen, icon_color, bat_cx, cy, self._battery_pct, self._battery_charging
        )

        # Battery % label (right of icon, above baseline)
        if self._battery_pct is not None:
            pct_str = f"{self._battery_pct}%"
            pct_surf = self.font_status.render(pct_str, True, icon_color)
            # small label sits just below the battery icon
            screen.blit(pct_surf, (bat_cx - pct_surf.get_width() // 2, cy + 8))
