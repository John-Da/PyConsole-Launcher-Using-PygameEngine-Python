
import pygame
import os
import sys
import json
import zipfile
import io
import time
import tempfile
import shutil
import importlib.util
import math


from utils.helpers import load_settings, save_settings, handle_navigation, get_stable_directory, get_app_path, \
    terminate, resource_path, load_app_metadata
from services.input_manager import InputManager
from ui.components import fade_screen, draw_loading_screen, booting_animation, draw_round_rect, draw_console_btn
from ui.virtual_keyboard import VirtualKeyboard

pygame.init()
pygame.joystick.init()

# ==========================
# CONSOLE THEMES
# ==========================
THEMES = [
    {"name": "MIDNIGHT", "bg": (18, 18, 24), "header": (32, 32, 40), "accent": (0, 255, 150), "text": (245, 245, 245),
     "btn": (60, 60, 75)},
    {"name": "SWITCH NEON", "bg": (235, 235, 235), "header": (255, 255, 255), "accent": (255, 60, 60),
     "text": (45, 45, 45), "btn": (0, 190, 255)},
    {"name": "3DS WHITE", "bg": (245, 245, 245), "header": (255, 255, 255), "accent": (160, 160, 160),
     "text": (70, 70, 70), "btn": (120, 120, 120)},
    {"name": "GAMEBOY", "bg": (155, 188, 15), "header": (139, 172, 15), "accent": (48, 98, 48), "text": (15, 56, 15),
     "btn": (48, 98, 48)},
    {"name": "KAWAII", "bg": (255, 245, 250), "header": (255, 255, 255), "accent": (255, 120, 190),
     "text": (110, 60, 60), "btn": (255, 190, 210)}
]



APP_NAME, APP_VERSION, APP_AUTHOR, APP_DESCRIPTION = load_app_metadata("config/metadata.json")

# joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
joysticks = {}
joy_delay = 0

WIDTH, HEIGHT = (800, 480)
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED | pygame.RESIZABLE)
pygame.display.set_caption(f"{APP_NAME} {APP_VERSION}")
clock = pygame.time.Clock()

# Use these paths throughout your script
APP_DATA_DIR, LIBRARY_FOLDER = get_app_path()
SETTINGS_FILE = os.path.join(APP_DATA_DIR, "config/settings.json")
LIBRARY_CACHE_DIR = os.path.join(APP_DATA_DIR, "cache/library_cache.json")

# STATE
current_theme_idx = 0

STATE_BOOT = "boot"
STATE_SHELL = "shell"
STATE_GAME = "game"

app_state = STATE_BOOT
pending_game = None

search_query = ""
selected = 0
focus_mode = "games"
view_mode = "grid"
button_selected = 0
scroll_y, target_scroll_y = 0, 0

# FONTS
font_main = pygame.font.SysFont("arial", 18, bold=True)
font_ui = pygame.font.SysFont("arial", 14, bold=True)
font_title = pygame.font.SysFont("arial", 58, bold=True)
font_badge = pygame.font.SysFont("arial", 14, bold=True)
font_ver = pygame.font.SysFont("arial", 14, bold=False)
font_meta = pygame.font.SysFont("arial", 12, bold=False)


# ==========================
# LAUNCHING FUNCTIONS
# ==========================

def launch_game(game_data, current_theme):
    global screen

    W, H = screen.get_size()
    fade_screen(screen, W, H, direction='in', speed=10)
    fade_screen(screen, W, H, direction='out', speed=10)
    draw_loading_screen(screen,clock, font_main, current_theme,f"BOOTING {game_data['name'].upper()}...")

    temp_dir = tempfile.mkdtemp(prefix="pyconsole_run_")
    original_cwd = os.getcwd()
    original_path = sys.path.copy()

    try:
        with zipfile.ZipFile(game_data["path"], 'r') as z:
            z.extractall(temp_dir)

        target_entry = game_data.get("entry", "main.py")
        script_path = None
        for root, dirs, files in os.walk(temp_dir):
            if target_entry in files:
                script_path = os.path.join(root, target_entry)
                sys.path.insert(0, root)
                os.chdir(root)
                break

        if script_path:
            spec = importlib.util.spec_from_file_location("game_run", script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, 'Game'):
                game_instance = module.Game(screen)
                game_instance.run()
            elif hasattr(module, 'create_game'):
                module.create_game(screen)

    except Exception as e:
        print(f"Game Crash: {e}")

    finally:
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except:
            pass

        fade_screen(screen, W, H, direction='out', speed=10)
        draw_loading_screen(screen, clock, font_main, current_theme, f"RETURNING TO {APP_NAME.upper()}...")

        os.chdir(original_cwd)
        sys.path = original_path
        shutil.rmtree(temp_dir, ignore_errors=True)

        pygame.display.quit()
        pygame.display.init()
        pygame.font.init()

        screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.SCALED | pygame.RESIZABLE)
        pygame.display.set_caption(f"PyConsole {APP_VERSION}")
        pygame.event.clear()

        screen.fill(current_theme["bg"])
        pygame.display.flip()


def load_games(path):
    loaded = []
    if not os.path.exists(path): return loaded
    for filename in os.listdir(path):
        if filename.endswith((".pgame", ".pygame", ".pgp", ".pypkg")):
            p = os.path.join(path, filename)
            game_icon = None
            meta = {"title": filename[:-7].replace("_", " "), "author": "Unknown", "version": "1.0", "entry": "main.py"}
            try:
                with zipfile.ZipFile(p, 'r') as z:
                    file_list = z.namelist()
                    meta_p = next((f for f in file_list if f.endswith('meta.json')), None)
                    icon_p = next((f for f in file_list if f.endswith('icon.png')), None) # icons/icon.png
                    if meta_p:
                        with z.open(meta_p) as f: meta.update(json.load(f))
                    if icon_p:
                        with z.open(icon_p) as f:
                            game_icon = pygame.image.load(io.BytesIO(f.read())).convert_alpha()
            except:
                pass
            loaded.append({
                "name": meta["title"], "author": meta["author"], "version": meta["version"],
                "entry": meta["entry"], "path": p, "icon": game_icon,
                "size": f"{os.path.getsize(p) / (1024 * 1024):.1f} MB"
            })
    return loaded


# ==========================
# MAIN LOOP
# ==========================
vk = VirtualKeyboard(fontstyle=font_ui)
input_manager = InputManager(joysticks)
LIBRARY_FOLDER, current_theme_idx, view_mode = load_settings(
    SETTINGS_FILE,
    LIBRARY_FOLDER,
    current_theme_idx,
    view_mode
)
games = load_games(LIBRARY_FOLDER)
booting_music = resource_path("assets", "sounds", "booting.wav")
boot_played = False

cursor_type = pygame.SYSTEM_CURSOR_ARROW
hovering_game = False
hovering_button = False

running = True
while running:
    theme = THEMES[current_theme_idx]
    W, H = screen.get_size()
    cursor_type = pygame.SYSTEM_CURSOR_ARROW


    result = input_manager.process_events(W, H)
    if result == "QUIT":
        terminate()

    m_pos = input_manager.actions["MOUSE_POS"]

    # =====================
    # STATE ROUTER
    # =====================
    if app_state == STATE_BOOT:
        if not boot_played:
            booting_animation(screen, clock, APP_NAME, booting_music, font_main, THEMES, current_theme_idx, 15)
            boot_played = True

        app_state = STATE_SHELL
        continue

    if app_state == STATE_GAME:
        launch_game(pending_game, theme)
        pending_game = None
        app_state = STATE_SHELL
        continue

    box_size, grid_gutter = 180, 25
    SIDE_M = 30
    cols = max(1, int((W - (SIDE_M * 2)) // (box_size + grid_gutter))) if view_mode == "grid" else 1

    filtered = [g for g in games if search_query.lower() in g["name"].lower()]
    screen.fill(theme["bg"])

    SIDE_M, HEADER_H = 60, 170
    BTN_H, BTN_W, GUTTER = 45, 90, 15

    # BUTTON RECTS
    exit_rect = pygame.Rect(W - SIDE_M - BTN_W, 35, BTN_W, BTN_H)
    list_rect = pygame.Rect(exit_rect.x - (BTN_W + GUTTER), 35, BTN_W, BTN_H)
    grid_rect = pygame.Rect(list_rect.x - (BTN_W + GUTTER), 35, BTN_W, BTN_H)
    theme_rect = pygame.Rect(grid_rect.x - (BTN_W + GUTTER), 35, BTN_W, BTN_H)
    add_rect = pygame.Rect(theme_rect.x, 95, BTN_W, BTN_H)
    search_bar_rect = pygame.Rect(add_rect.right + GUTTER, 95, exit_rect.right - (add_rect.right + GUTTER), BTN_H)
    search_btn_rect = pygame.Rect(search_bar_rect.x + 5, search_bar_rect.y + 5, 75, BTN_H - 10)

    hovering_button = False
    if input_manager.last_input in ("mouse", "touch"):
        # reset hover focus first
        if not (theme_rect.collidepoint(m_pos) or
                grid_rect.collidepoint(m_pos) or
                list_rect.collidepoint(m_pos) or
                exit_rect.collidepoint(m_pos) or
                add_rect.collidepoint(m_pos) or
                search_btn_rect.collidepoint(m_pos)):
            if focus_mode in ("top_bar", "buttons"):
                focus_mode = "games"

    if input_manager.last_input in ("mouse", "touch"):
        if theme_rect.collidepoint(m_pos):
            focus_mode = "top_bar"
            button_selected = 1
            hovering_button = True

        elif grid_rect.collidepoint(m_pos):
            focus_mode = "top_bar"
            button_selected = 2
            hovering_button = True

        elif list_rect.collidepoint(m_pos):
            focus_mode = "top_bar"
            button_selected = 3
            hovering_button = True

        elif exit_rect.collidepoint(m_pos):
            focus_mode = "top_bar"
            button_selected = 4
            hovering_button = True

        elif add_rect.collidepoint(m_pos):
            focus_mode = "buttons"
            button_selected = 0
            hovering_button = True

        elif search_btn_rect.collidepoint(m_pos):
            focus_mode = "buttons"
            button_selected = 5
            hovering_button = True


    if hovering_button or hovering_game:
        cursor_type = pygame.SYSTEM_CURSOR_HAND


    if vk.active:
        action = None
        for a in ["UP", "DOWN", "LEFT", "RIGHT", "ACCEPT"]:
            if input_manager.actions[a]: action = a

        vk.handle_input(action, m_pos, input_manager.actions["CLICK"])
        search_query = vk.output
        if input_manager.actions["BACK"]:
            vk.active = False

    else:
        for act in ["UP", "DOWN", "LEFT", "RIGHT"]:
            if input_manager.actions[act]:
                focus_mode, button_selected, selected = handle_navigation(
                    focus_mode, button_selected, selected, act, cols, len(filtered)
                )

        if input_manager.actions["BACK"]: focus_mode = "games"

        if input_manager.actions["ACCEPT"]:
            if search_bar_rect.collidepoint(m_pos) or (focus_mode == "buttons" and button_selected == 5):
                vk.active = True
                vk.output = search_query

        # Selection Logic
        m_pos = input_manager.actions["MOUSE_POS"]
        if input_manager.actions["ACCEPT"]:

            if theme_rect.collidepoint(m_pos) or (focus_mode == "top_bar" and button_selected == 1):
                current_theme_idx = (current_theme_idx + 1) % len(THEMES)
                save_settings(SETTINGS_FILE, LIBRARY_FOLDER, current_theme_idx, view_mode)

            elif grid_rect.collidepoint(m_pos) or (focus_mode == "top_bar" and button_selected == 2):
                view_mode = "grid"
                save_settings(SETTINGS_FILE, LIBRARY_FOLDER, current_theme_idx, view_mode)

            elif list_rect.collidepoint(m_pos) or (focus_mode == "top_bar" and button_selected == 3):
                view_mode = "list"
                save_settings(SETTINGS_FILE, LIBRARY_FOLDER, current_theme_idx, view_mode)

            elif exit_rect.collidepoint(m_pos) or (focus_mode == "top_bar" and button_selected == 4):
                save_settings(SETTINGS_FILE, LIBRARY_FOLDER, current_theme_idx, view_mode)
                draw_loading_screen(screen, clock, font_main, theme, f"CLOSING {APP_NAME.upper()}...")
                pygame.mixer.music.load(booting_music)
                pygame.mixer.music.set_volume(0.7)
                pygame.mixer.music.play(fade_ms=300)
                pygame.time.wait(5500)
                fade_screen(screen, W, H, direction='out', speed=10)
                running = False
                terminate()

            elif add_rect.collidepoint(m_pos) or (focus_mode == "buttons" and button_selected == 0):
                p = get_stable_directory()
                if p: LIBRARY_FOLDER = p; games = load_games(p)
            elif search_bar_rect.collidepoint(m_pos) or (focus_mode == "buttons" and button_selected == 5):
                focus_mode = "search"
            elif focus_mode == "games" and filtered:
                if not input_manager.actions["CLICK"] or m_pos[1] > HEADER_H:
                    # launch_game(filtered[selected], theme)
                    pending_game = filtered[selected]
                    app_state = STATE_GAME

        # Search Logic
        if focus_mode == "search" and input_manager.actions["ANY_KEY"]:
            ev = input_manager.actions["ANY_KEY"]
            if ev.key == pygame.K_BACKSPACE:
                search_query = search_query[:-1]
            elif ev.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                focus_mode = "games"
            else:
                search_query += ev.unicode
                selected = 0

        if view_mode == "grid":
            rows = math.ceil(len(filtered) / cols)
            total_content_h = (HEADER_H + 50) + (rows * (box_size + 60))
        else:
            item_h = 85
            total_content_h = (HEADER_H + 30) + (len(filtered) * (item_h + 10))

        max_scroll = max(0, total_content_h - H + 100)
        if target_scroll_y > max_scroll: target_scroll_y = max_scroll
        if target_scroll_y < 0: target_scroll_y = 0
        scroll_y += (target_scroll_y - scroll_y) * 0.1

        if view_mode == "grid":
            start_x = (W - ((cols * box_size) + ((cols - 1) * grid_gutter))) // 2
            for i, g in enumerate(filtered):
                col, row = i % cols, i // cols
                x = start_x + col * (box_size + grid_gutter) + box_size // 2
                y = (HEADER_H + 130) + row * (box_size + 60) - scroll_y

                if -250 < y < H + 250:
                    rect = pygame.Rect(0, 0, box_size, box_size)
                    rect.center = (x, y)

                    # Mouse Hover
                    if input_manager.last_input in ("mouse", "touch"):
                        if rect.collidepoint(m_pos) and m_pos[1] > HEADER_H:
                            selected, focus_mode = i, "games"
                            hovering_game = True

                    is_sel = (i == selected and focus_mode == "games")

                    # Auto-Scroll Logic: Keep selection in view
                    if is_sel:
                        if rect.bottom > H - 50: target_scroll_y += 10
                        if rect.top < HEADER_H + 50: target_scroll_y -= 10

                    draw_round_rect(screen, theme["header"], rect, 15)
                    if is_sel:
                        draw_round_rect(screen, theme["accent"], rect.inflate(10, 10), 18, 4)

                    if g["icon"]:
                        img = pygame.transform.smoothscale(g["icon"], (rect.width - 60, rect.height - 60))
                        screen.blit(img, img.get_rect(center=rect.center))

                    txt = font_main.render(g["name"], True, theme["text"])
                    screen.blit(txt, (x - txt.get_width() // 2, rect.bottom + 12))

        else:
            item_h = 85
            for i, g in enumerate(filtered):
                y = (HEADER_H + 30) + i * (item_h + 10) - scroll_y

                if -100 < y < H + 100:
                    rect = pygame.Rect(SIDE_M, y, W - SIDE_M * 2, item_h)

                    if input_manager.last_input in ("mouse", "touch"):
                        if rect.collidepoint(m_pos) and m_pos[1] > HEADER_H:
                            selected, focus_mode = i, "games"
                            hovering_game = True

                    is_sel = (i == selected and focus_mode == "games")

                    # Auto-Scroll Logic for List
                    if is_sel:
                        if rect.bottom > H - 20: target_scroll_y += 10
                        if rect.top < HEADER_H + 20: target_scroll_y -= 10

                    draw_round_rect(screen, theme["header"], rect, 12)
                    if is_sel: draw_round_rect(screen, theme["accent"], rect, 12, 3)

                    if g["icon"]:
                        img = pygame.transform.smoothscale(g["icon"], (60, 60))
                        screen.blit(img, (rect.x + 15, rect.y + 12))
                    screen.blit(font_main.render(g["name"], True, theme["text"]), (rect.x + 90, rect.y + 15))
                    screen.blit(font_meta.render(f"by {g['author']}  |  v{g['version']}", True, theme["text"]),
                                (rect.x + 90, rect.y + 40))

                    size_info = f"Size: {g['size']}"
                    screen.blit(font_ui.render(size_info, True, theme["accent"]), (rect.x + 90, rect.y + 58))


    # --- HEADER UI ---
    pygame.draw.rect(screen, theme["header"], (0, 0, W, HEADER_H))

    # Title
    title_surf = font_title.render(f"{APP_NAME}", True, theme["text"])
    screen.blit(title_surf, (SIDE_M, 35))

    info_str = f"{APP_VERSION}  |  {len(filtered)} Games Loaded"
    info_surf = font_ver.render(info_str, True, theme["text"])
    screen.blit(info_surf, (SIDE_M + 5, title_surf.get_height() + 45))

    pygame.draw.rect(screen, theme["accent"], (SIDE_M + 5, title_surf.get_height() + 65, 190, 3))

    # SEARCH & UTILS
    draw_round_rect(screen, theme["bg"], search_bar_rect, 10)

    is_theme_focused = (focus_mode == "top_bar" and button_selected == 1)
    draw_console_btn(screen, "THEME", theme_rect, is_theme_focused, font_ui, theme)

    is_grid_focused = (focus_mode == "top_bar" and button_selected == 2)
    draw_console_btn(screen, "GRID", grid_rect, is_grid_focused, font_ui, theme)

    is_list_focused = (focus_mode == "top_bar" and button_selected == 3)
    draw_console_btn(screen, "LIST", list_rect, is_list_focused, font_ui, theme)

    is_exit_focused = (focus_mode == "top_bar" and button_selected == 4)
    draw_console_btn(screen, "EXIT", exit_rect, is_exit_focused, font_ui, theme)

    draw_console_btn(screen, "+ ADD", add_rect, (focus_mode == "buttons" and button_selected == 0), font_ui, theme)
    draw_console_btn(screen, "SEARCH", search_btn_rect, (focus_mode == "buttons" and button_selected == 5), font_ui, theme)

    stxt = search_query + (
        "|" if focus_mode == "search" and time.time() % 1 > 0.5 else "") if search_query or focus_mode == "search" else "Search library..."
    screen.blit(font_main.render(stxt, True, theme["text"]), (search_btn_rect.right + 15, search_bar_rect.y + 10))

    target_scroll_y = max(0, target_scroll_y)

    if vk.active:
        vk.draw(screen, theme)

    pygame.mouse.set_cursor(cursor_type)

    pygame.display.flip()
    clock.tick(60)

terminate()

