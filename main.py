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

from system.system_manager import SystemManager

from services.input_manager import InputManager
from services.game_manager import GameManager
from services.theme_manager import ThemeManager

from screens.games import GamesScreen
from screens.settings import SettingsScreen

from ui.components import booting_animation, shutdown_animation
from ui.virtual_keyboard import VirtualKeyboard
from ui.footer import Footer
from ui.navbar import NavBar, TAB_GAMES, TAB_STORE, TAB_SETTINGS, TABS
from ui.widgets import Widgets
from ui.logo import AnimatedLogo

pygame.init()
pygame.joystick.init()

# ==========================
# CONSOLE CONFIG
# ==========================

APP_NAME, APP_VERSION, APP_AUTHOR, APP_DESCRIPTION = load_app_metadata(
    "config/metadata.json"
)

joysticks = {}

# Populate already-connected controllers immediately.
# JOYDEVICEADDED events for pre-connected devices can be
# consumed/lost by pygame.event.get() calls during boot animation.
for i in range(pygame.joystick.get_count()):
    joy = pygame.joystick.Joystick(i)
    joy.init()
    joysticks[joy.get_instance_id()] = joy

WIDTH, HEIGHT = 800, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.FULLSCREEN)
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
view_mode = "grid"
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
theme_manager = ThemeManager(resource_path_fn=resource_path)
theme_manager.set_index(current_theme_idx)

splash_logo = AnimatedLogo(
    resource_path("assets", "images", "logo_frames"),
    max_height=40,
    frame_duration=0.1,
)

vk = VirtualKeyboard(fontstyle=font_ui)
input_manager = InputManager(joysticks)

# Load saved settings (library path, theme index, view mode, profile, render quality)
LIBRARY_FOLDER, current_theme_idx, view_mode, perf_profile, render_quality = (
    load_settings(SETTINGS_FILE, LIBRARY_FOLDER, current_theme_idx, view_mode)
)

# Apply theme index loaded from settings (theme_manager was created above with default index 0)
theme_manager.set_index(current_theme_idx)

system_manager = SystemManager(os_version=APP_VERSION)
system_manager.profile.set_profile(perf_profile)
system_manager.profile.render_quality = render_quality

game_manager = GameManager(LIBRARY_FOLDER)
booting_music = resource_path("assets", "sounds", "startup.wav")
closing_music = resource_path("assets", "sounds", "error.wav")
boot_played = False

cursor_type = pygame.SYSTEM_CURSOR_ARROW

font_icon = pygame.font.Font(
    resource_path("assets", "fonts", "MaterialIcons-Regular.ttf"), NavBar.ICON_SIZE
)
navbar = NavBar(
    font_tab=font_ui,
    font_status=font_meta,
    font_icon=font_icon,
    logo_path=resource_path("assets", "images", "logo_frames"),
    frame_duration=0.1,
)

games_screen = GamesScreen(font_main, font_meta, font_ui)


def persist_settings():
    save_settings(
        SETTINGS_FILE,
        settings_screen.library_folder,
        theme_manager.current_index,
        view_mode,
        performance_profile=system_manager.profile.name,
        render_quality=system_manager.profile.render_quality,
    )


settings_screen = SettingsScreen(
    font_main,
    font_meta,
    font_ui,
    system_manager,
    theme_manager,
    library_folder=LIBRARY_FOLDER,
    vk=vk,
    on_library_path_change=lambda new_path: game_manager.set_library_folder(new_path),
    on_settings_changed=persist_settings,
)

footer = Footer(
    font_badge=font_badge,
    font_label=font_ui,
    app_version=APP_VERSION,
)

widgets = Widgets(font_main, font_ui, font_meta)

# ==========================
# MAIN LOOP
# ==========================
running = True
while running:

    W, H = screen.get_size()
    cursor_type = pygame.SYSTEM_CURSOR_ARROW

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
                theme_manager.themes,
                theme_manager.current_index,
                15,
                boot_logo=splash_logo,
            )
            boot_played = True
        app_state = STATE_SHELL
        clock.tick(60)
        continue

    dt = clock.get_time() / 1000.0
    theme_manager.update(dt)
    theme = theme_manager.current

    navbar.update_layout(W)
    games_screen.info_panel.update(dt)
    system_manager.update()
    footer.update_layout(W)

    result = input_manager.process_events(W, H)
    if result == "QUIT":
        shutdown_animation(
            screen,
            clock,
            APP_NAME,
            closing_music,
            font_main,
            theme,
            shutdown_logo=splash_logo,
        )
        terminate()

    m_pos = input_manager.actions["MOUSE_POS"]

    # DEBUG: uncomment to confirm whether input is reaching this point
    # print("actions:", input_manager.actions, "| vk.active:", vk.active,
    #       "| modal_open:", widgets.is_modal_open)

    if app_state == STATE_GAME:
        game_manager.select(pending_game)
        screen = game_manager.launch(screen, clock, font_main, theme, APP_NAME)
        # print(f"screen after launch: {screen}")
        pending_game = None
        app_state = STATE_SHELL
        continue

    # =====================
    # FILTER GAMES
    # =====================
    filtered = game_manager.filter(search_query)
    theme.draw_background(screen)

    # =====================
    # INPUT HANDLING
    # =====================
    nav_clicked = False

    if widgets.is_modal_open:
        if widgets.power_menu_open:
            choice = widgets.handle_power_input(input_manager.actions)
            if choice == "Sleep":
                ...
            elif choice == "Restart":
                ...
            elif choice == "Shutdown":
                shutdown_animation(
                    screen,
                    clock,
                    APP_NAME,
                    closing_music,
                    font_main,
                    theme,
                    shutdown_logo=splash_logo,
                )
                terminate()
        elif widgets.notification:
            widgets.handle_notification_input(input_manager.actions)

    else:
        if input_manager.actions["POWER_MENU"]:
            widgets.open_power_menu()

        if vk.active:
            action = None
            for a in ["UP", "DOWN", "LEFT", "RIGHT", "ACCEPT"]:
                if input_manager.actions[a]:
                    action = a

            vk.handle_input(action, m_pos, input_manager.actions["CLICK"])

            if getattr(settings_screen, "_editing_library_path", False):
                pass  # vk.output is the path, don't touch search_query
            else:
                search_query = vk.output

            if input_manager.actions["BACK"]:
                vk.active = False
                settings_screen.finish_library_path_edit()

        else:
            # --- NavBar tab switching (mouse/touch click) ---
            if input_manager.actions["ACCEPT"]:
                nav_result = navbar.handle_click(m_pos)
                if "tab" in nav_result:
                    active_tab = nav_result["tab"]
                    games_screen.info_panel.close()
                    settings_screen.reset()
                    nav_clicked = True

            # --- Tab switching via L/R shoulder buttons ---
            if input_manager.actions["TAB_LEFT"]:
                idx = TABS.index(active_tab)
                active_tab = TABS[(idx - 1) % len(TABS)]
                games_screen.info_panel.close()
                settings_screen.reset()

            if input_manager.actions["TAB_RIGHT"]:
                idx = TABS.index(active_tab)
                active_tab = TABS[(idx + 1) % len(TABS)]
                games_screen.info_panel.close()
                settings_screen.reset()

            # --- Games tab input ---
            if active_tab == TAB_GAMES and not nav_clicked:
                selected = games_screen.handle_input(input_manager.actions, filtered)
                if selected:
                    # print(f"Selected game: {selected}")
                    pending_game = selected
                    app_state = STATE_GAME

    # =====================
    # DRAW: TAB CONTENT
    # =====================
    content_rect = pygame.Rect(0, NavBar.HEIGHT, W, H - NavBar.HEIGHT - Footer.HEIGHT)

    if active_tab == TAB_GAMES:
        games_screen.update(dt, filtered)
        games_screen.draw(screen, theme, filtered, content_rect, Footer.HEIGHT)

    elif active_tab == TAB_STORE:
        placeholder = font_main.render("Store — coming soon", True, theme["text"])
        screen.blit(placeholder, placeholder.get_rect(center=content_rect.center))

    elif active_tab == TAB_SETTINGS:
        if not nav_clicked:
            settings_screen.handle_input(input_manager.actions)
        settings_screen.update(dt)
        settings_screen.draw(screen, theme, content_rect, Footer.HEIGHT)

        if settings_screen.consume_power_menu_request():
            widgets.open_power_menu()

    # =====================
    # DRAW: NAVBAR + FOOTER
    # =====================
    navbar.draw(screen, theme, active_tab=active_tab, m_pos=m_pos, dt=dt)
    footer.draw(screen, theme)

    widgets.draw_power_menu(screen, theme)
    widgets.draw_notification(screen, theme)

    pygame.display.flip()
    clock.tick(60)

terminate()
