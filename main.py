import pygame
import os

from utils.helpers import (
    load_settings,
    save_settings,
    get_app_path,
    terminate,
    resource_path,
    load_app_metadata,
)
from services.input_manager import InputManager
from services.game_launcher import load_games, launch_game

from themes.system_theme import THEMES

from ui.components import booting_animation
from ui.virtual_keyboard import VirtualKeyboard
from ui.footer import Footer
from ui.navbar import NavBar, TAB_GAMES, TAB_STORE, TAB_SETTINGS, TABS
from ui.carousel import Carousel
from ui.info_panel import InfoPanel

pygame.init()
pygame.joystick.init()

# ==========================
# CONSOLE CONFIG
# ==========================

APP_NAME, APP_VERSION, APP_AUTHOR, APP_DESCRIPTION = load_app_metadata(
    "config/metadata.json"
)

joysticks = {}

WIDTH, HEIGHT = 800, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
pygame.display.set_caption(f"{APP_NAME} {APP_VERSION}")
clock = pygame.time.Clock()

# Paths
APP_DATA_DIR, LIBRARY_FOLDER = get_app_path()
SETTINGS_FILE = os.path.join(APP_DATA_DIR, "config/settings.json")

# STATE
STATE_BOOT = "boot"
STATE_SHELL = "shell"
STATE_GAME = "game"

app_state = STATE_BOOT
pending_game = None
current_theme_idx = 0
view_mode = "grid"  # kept for save_settings() compatibility; carousel ignores it
active_tab = TAB_GAMES

search_query = ""

# FONTS
font_main = pygame.font.SysFont("arial", 18, bold=True)
font_ui = pygame.font.SysFont("arial", 14, bold=True)
font_title = pygame.font.SysFont("arial", 58, bold=True)
font_badge = pygame.font.SysFont("arial", 14, bold=True)
font_ver = pygame.font.SysFont("arial", 14, bold=False)
font_meta = pygame.font.SysFont("arial", 12, bold=False)


# ==========================
# SETUP
# ==========================
vk = VirtualKeyboard(fontstyle=font_ui)
input_manager = InputManager(joysticks)
LIBRARY_FOLDER, current_theme_idx, view_mode = load_settings(
    SETTINGS_FILE, LIBRARY_FOLDER, current_theme_idx, view_mode
)
games = load_games(LIBRARY_FOLDER)
booting_music = resource_path("assets", "sounds", "startup.wav")
closing_music = resource_path("assets", "sounds", "closing.wav")
boot_played = False

cursor_type = pygame.SYSTEM_CURSOR_ARROW

navbar = NavBar(
    font_tab=font_ui,
    font_status=font_meta,
    logo_path=resource_path("assets", "images", "logo_frames"),
    frame_duration=0.1,
)

carousel = Carousel(font_title=font_main, font_meta=font_meta)
info_panel = InfoPanel(font_title=font_main, font_label=font_ui, font_body=font_meta)

footer = Footer(
    font_badge=font_badge,
    font_label=font_ui,
    app_version=APP_VERSION,
)

# ==========================
# MAIN LOOP
# ==========================
running = True
while running:
    theme = THEMES[current_theme_idx]
    W, H = screen.get_size()
    cursor_type = pygame.SYSTEM_CURSOR_ARROW

    dt = clock.get_time() / 1000.0
    navbar.update_layout(W)
    info_panel.update(dt)
    footer.update_layout(W)

    result = input_manager.process_events(W, H)
    if result == "QUIT":
        terminate()

    m_pos = input_manager.actions["MOUSE_POS"]

    # =====================
    # STATE ROUTER
    # =====================
    if app_state == STATE_BOOT:
        if not boot_played:
            booting_animation(
                screen,
                clock,
                APP_NAME,
                booting_music,
                font_main,
                THEMES,
                current_theme_idx,
                15,
            )
            boot_played = True
        app_state = STATE_SHELL
        continue

    if app_state == STATE_GAME:
        screen = launch_game(screen, clock, font_main, pending_game, theme, APP_NAME)
        pending_game = None
        app_state = STATE_SHELL
        continue

    # =====================
    # FILTER GAMES
    # =====================
    filtered = [g for g in games if search_query.lower() in g["name"].lower()]
    screen.fill(theme["bg"])

    # Keep carousel selection valid if the filtered list shrinks/grows
    if carousel.selected >= len(filtered):
        carousel.set_selected(max(0, len(filtered) - 1), len(filtered))

    # =====================
    # INPUT HANDLING
    # =====================
    if vk.active:
        action = None
        for a in ["UP", "DOWN", "LEFT", "RIGHT", "ACCEPT"]:
            if input_manager.actions[a]:
                action = a

        vk.handle_input(action, m_pos, input_manager.actions["CLICK"])
        search_query = vk.output
        if input_manager.actions["BACK"]:
            vk.active = False

    else:
        # --- NavBar tab switching (mouse/touch click) ---
        if input_manager.actions["ACCEPT"]:
            nav_result = navbar.handle_click(m_pos)
            if "tab" in nav_result:
                active_tab = nav_result["tab"]
                info_panel.close()

        # --- Tab switching via L/R shoulder buttons (any tab) ---
        if input_manager.actions["TAB_LEFT"]:
            idx = TABS.index(active_tab)
            active_tab = TABS[(idx - 1) % len(TABS)]
            info_panel.close()

        if input_manager.actions["TAB_RIGHT"]:
            idx = TABS.index(active_tab)
            active_tab = TABS[(idx + 1) % len(TABS)]
            info_panel.close()

        # --- Games tab: carousel navigation ---
        if active_tab == TAB_GAMES:
            if input_manager.actions["LEFT"]:
                carousel.move_left(len(filtered))
                info_panel.close()
            if input_manager.actions["RIGHT"]:
                carousel.move_right(len(filtered))
                info_panel.close()

            if input_manager.actions["ACCEPT"]:
                game = carousel.get_selected_game(filtered)
                if game:
                    pending_game = game
                    app_state = STATE_GAME

            if input_manager.actions["DETAIL"]:
                game = carousel.get_selected_game(filtered)
                if game:
                    info_panel.toggle(game)

        if input_manager.actions["BACK"] and info_panel.is_open:
            info_panel.close()

    # =====================
    # DRAW: TAB CONTENT
    # =====================
    content_rect = pygame.Rect(0, NavBar.HEIGHT, W, H - NavBar.HEIGHT - Footer.HEIGHT)

    if active_tab == TAB_GAMES:
        carousel.update(dt)
        carousel.draw(screen, theme, filtered, content_rect)

    elif active_tab == TAB_STORE:
        placeholder = font_main.render("Store — coming soon", True, theme["text"])
        screen.blit(placeholder, placeholder.get_rect(center=content_rect.center))

    elif active_tab == TAB_SETTINGS:
        placeholder = font_main.render("Settings — coming soon", True, theme["text"])
        screen.blit(placeholder, placeholder.get_rect(center=content_rect.center))

    # =====================
    # DRAW: NAVBAR + FOOTER
    # =====================
    navbar.draw(screen, theme, active_tab=active_tab, m_pos=m_pos, dt=dt)
    info_panel.draw(screen, theme, footer_height=Footer.HEIGHT)
    footer.draw(screen, theme)

    pygame.display.flip()
    clock.tick(60)

terminate()
