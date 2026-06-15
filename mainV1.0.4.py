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
import subprocess
import tkinter as tk
from tkinter import filedialog

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

APP_VERSION = "v1.0.4-stable"

pygame.init()
pygame.joystick.init()

# joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
joysticks = {}
joy_delay = 0

WIDTH, HEIGHT = (1200, 800)
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED | pygame.RESIZABLE)
pygame.display.set_caption(f"PyConsole {APP_VERSION}")
clock = pygame.time.Clock()


def get_app_path():
    if sys.platform == "win32":
        # Windows: C:\Users\Name\AppData\Roaming\PyConsole
        base_path = os.path.join(os.environ.get('APPDATA'), "PyConsole")
    elif sys.platform == "darwin":
        # Mac: /Users/Name/Library/Application Support/PyConsole
        base_path = os.path.expanduser("~/Library/Application Support/PyConsole")
    else:
        # Linux: /home/Name/.pyconsole
        base_path = os.path.expanduser("~/.pyconsole")

    # Create the folders if they don't exist
    games_path = os.path.join(base_path, "games")
    if not os.path.exists(games_path):
        os.makedirs(games_path)

    return base_path, games_path

# Use these paths throughout your script
APP_DATA_DIR, LIBRARY_FOLDER = get_app_path()
SETTINGS_FILE = os.path.join(APP_DATA_DIR, "settings.json")

# STATE
current_theme_idx = 0
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
# FUNCTIONS
# ==========================

def save_settings():
    config = {
        "library_path": LIBRARY_FOLDER,
        "theme_index": current_theme_idx,
        "view_mode": view_mode
    }
    with open(SETTINGS_FILE, "w") as f:
        json.dump(config, f)


def load_settings():
    global LIBRARY_FOLDER, current_theme_idx, view_mode
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                config = json.load(f)
                LIBRARY_FOLDER = config.get("library_path", LIBRARY_FOLDER)
                current_theme_idx = config.get("theme_index", 0)
                view_mode = config.get("view_mode", "grid")
        except:
            print("Settings file corrupted, using defaults.")


def handle_navigation(key_event, cols, total_games):
    global focus_mode, button_selected, selected, current_theme_idx, view_mode, running, search_query, games, LIBRARY_FOLDER

    if focus_mode == "buttons":
        if key_event == pygame.K_UP:
            focus_mode = "top_bar"
            button_selected = 1
        elif key_event == pygame.K_DOWN:
            focus_mode = "games"
            selected = 0
        elif key_event == pygame.K_LEFT:
            button_selected = 0 if button_selected == 5 else 5
        elif key_event == pygame.K_RIGHT:
            button_selected = 5 if button_selected == 0 else 0

    elif focus_mode == "top_bar":
        if key_event == pygame.K_DOWN:
            focus_mode = "buttons";
            button_selected = 0
        elif key_event == pygame.K_LEFT:
            button_selected = max(1, button_selected - 1)
        elif key_event == pygame.K_RIGHT:
            button_selected = min(4, button_selected + 1)

    elif focus_mode == "games":
        if key_event == pygame.K_UP:
            if selected < cols:
                focus_mode = "buttons"
                button_selected = 0
            else:
                selected -= cols
        elif key_event == pygame.K_DOWN:
            if selected + cols < total_games:
                selected += cols

        elif key_event == pygame.K_LEFT:
            selected = max(0, selected - 1)
        elif key_event == pygame.K_RIGHT:
            selected = min(len(filtered) - 1, selected + 1)


def draw_round_rect(surf, color, rect, radius=10, border=0):
    if rect.width <= 0 or rect.height <= 0: return
    pygame.draw.rect(surf, color, rect, border, border_radius=radius)


def draw_loading_screen(text="LOADING", total_duration=11000, theme=THEMES[0]):

    start_time = pygame.time.get_ticks()
    loading = True

    while loading:
        current_ticks = pygame.time.get_ticks()
        elapsed = current_ticks - start_time

        if elapsed < 1000:  # 0 → 15%
            progress = (elapsed / 1000) * 0.15

        elif elapsed < 4000:  # pause 3s
            progress = 0.15

        elif elapsed < 5000:  # 15 → 78%
            progress = 0.15 + ((elapsed - 4000) / 1000) * (0.78 - 0.15)

        elif elapsed < 6000:  # pause 1s
            progress = 0.78

        elif elapsed < 7000:  # 78 → 97%
            progress = 0.78 + ((elapsed - 6000) / 1000) * (0.97 - 0.78)

        elif elapsed < 8500:  # pause 1.5s
            progress = 0.97

        elif elapsed < 9500:  # 97 → 100%
            progress = 0.97 + ((elapsed - 8500) / 1000) * (1.0 - 0.97)

        else:
            progress = 1.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()

        screen.fill(theme["bg"])
        bar_w, bar_h = 400, 8
        bar_x, bar_y = (screen.get_width() - bar_w) // 2, (screen.get_height() // 2) + 40

        # Draw Bar
        draw_round_rect(screen, theme["header"], pygame.Rect(bar_x, bar_y, bar_w, bar_h), 4)
        draw_round_rect(screen, theme["accent"], pygame.Rect(bar_x, bar_y, int(bar_w * progress), bar_h), 4)

        # Pulsing Text
        alpha = int(155 + 100 * math.sin(current_ticks * 0.006))
        txt_surf = font_main.render(text, True, theme["text"])
        txt_surf.set_alpha(alpha)
        screen.blit(txt_surf, (screen.get_width() // 2 - txt_surf.get_width() // 2, bar_y - 40))

        pygame.display.flip()
        clock.tick(60)
        if progress >= 1.0: loading = False


def fade_screen(width, height, direction='out', speed=5):

    fade_surf = pygame.Surface((width, height))
    fade_surf.fill((0, 0, 0))
    if direction == 'out':
        for alpha in range(0, 256, speed):
            fade_surf.set_alpha(alpha)
            screen.blit(fade_surf, (0, 0))
            pygame.display.flip()
            pygame.time.delay(10)
    else:
        for alpha in range(256, 0, -speed):
            fade_surf.set_alpha(alpha)
            screen.blit(fade_surf, (0, 0))
            pygame.display.flip()
            pygame.time.delay(10)


def launch_game(game_data, current_theme):
    global screen

    W, H = screen.get_size()
    fade_screen(W, H, direction='in', speed=10)
    fade_screen(W, H, direction='out', speed=10)
    draw_loading_screen(f"BOOTING {game_data['name'].upper()}...", 1500, current_theme)

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

        fade_screen(W, H, direction='out', speed=10)
        draw_loading_screen("RETURNING TO PYCONSOLE...", 800, current_theme)

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


def get_stable_directory():
    if sys.platform == "darwin":
        try:
            script = 'posix path of (choose folder with prompt "Select Games Folder")'
            proc = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            if proc.returncode == 0:
                return proc.stdout.strip()
            return None
        except Exception as e:
            print(f"AppleScript Error: {e}")
            return None
    else:
        # Keep the Tkinter version for Windows/Linux
        try:
            root = tk.Tk(); root.withdraw(); root.attributes('-topmost', True)
            path = filedialog.askdirectory(title="Select Games Folder")
            root.destroy()
            return path
        except:
            return None


def load_games(path):
    loaded = []
    if not os.path.exists(path): return loaded
    for filename in os.listdir(path):
        if filename.endswith((".pgame", ".pygame")):
            p = os.path.join(path, filename)
            game_icon = None
            meta = {"title": filename[:-7].replace("_", " "), "author": "Unknown", "version": "1.0", "entry": "main.py"}
            try:
                with zipfile.ZipFile(p, 'r') as z:
                    file_list = z.namelist()
                    meta_p = next((f for f in file_list if f.endswith('meta.json')), None)
                    icon_p = next((f for f in file_list if f.endswith('icon.png')), None)
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


def draw_console_btn(surf, text, rect, focused, theme, radius=10):
    bg = theme["accent"] if focused else theme["header"]
    txt_color = theme["bg"] if focused else theme["text"]
    draw_round_rect(surf, bg, rect, radius)
    if not focused: draw_round_rect(surf, theme["accent"], rect, radius, 2)
    t_surf = font_ui.render(text.upper(), True, txt_color)
    surf.blit(t_surf, t_surf.get_rect(center=rect.center))


# ==========================
# MAIN LOOP
# ==========================
running = True
load_settings()
games = load_games(LIBRARY_FOLDER)

while running:
    theme = THEMES[current_theme_idx]
    W, H = screen.get_size()
    box_size, grid_gutter = 180, 25
    SIDE_M = 30
    cols = max(1, int((W - (SIDE_M * 2)) // (box_size + grid_gutter))) if view_mode == "grid" else 1

    filtered = [g for g in games if search_query.lower() in g["name"].lower()]
    scroll_y += (target_scroll_y - scroll_y) * 0.1
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

    # CONTENT RENDERING
    if view_mode == "grid":
        start_x = (W - ((cols * box_size) + ((cols - 1) * grid_gutter))) // 2
        for i, g in enumerate(filtered):
            col, row = i % cols, i // cols
            x, y = start_x + col * (box_size + grid_gutter) + box_size // 2, HEADER_H + 130 + row * (
                        box_size + 60) - scroll_y
            if -250 < y < H + 250:
                is_sel = (i == selected and focus_mode == "games")
                rect = pygame.Rect(0, 0, box_size, box_size)
                rect.center = (x, y)
                draw_round_rect(screen, theme["header"], rect, 15)
                if is_sel: draw_round_rect(screen, theme["accent"], rect.inflate(10, 10), 18, 4)
                if g["icon"]:
                    img = pygame.transform.smoothscale(g["icon"], (rect.width - 60, rect.height - 60))
                    screen.blit(img, img.get_rect(center=rect.center))
                txt = font_main.render(g["name"], True, theme["text"])
                screen.blit(txt, (x - txt.get_width() // 2, rect.bottom + 12))
    else:
        item_h = 85
        cols = 1
        for i, g in enumerate(filtered):
            y = HEADER_H + 30 + i * (item_h + 10) - scroll_y
            if -100 < y < H + 100:
                is_sel = (i == selected and focus_mode == "games")
                rect = pygame.Rect(SIDE_M, y, W - SIDE_M * 2, item_h)
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
    title_surf = font_title.render("PyConsole", True, theme["text"])
    screen.blit(title_surf, (SIDE_M, 35))

    info_str = f"{APP_VERSION}  |  {len(filtered)} Games Loaded"
    info_surf = font_ver.render(info_str, True, theme["text"])
    screen.blit(info_surf, (SIDE_M + 5, title_surf.get_height() + 45))

    pygame.draw.rect(screen, theme["accent"], (SIDE_M + 5, title_surf.get_height() + 65, 190, 3))

    # SEARCH & UTILS
    draw_round_rect(screen, theme["bg"], search_bar_rect, 10)

    is_theme_focused = (focus_mode == "top_bar" and button_selected == 1) or (
            view_mode == "button" and focus_mode == "games")
    draw_console_btn(screen, "THEME", theme_rect, is_theme_focused, theme)

    is_grid_focused = (focus_mode == "top_bar" and button_selected == 2) or (
                view_mode == "grid" and focus_mode == "games")
    draw_console_btn(screen, "GRID", grid_rect, is_grid_focused, theme)

    is_list_focused = (focus_mode == "top_bar" and button_selected == 3) or (
                view_mode == "list" and focus_mode == "games")
    draw_console_btn(screen, "LIST", list_rect, is_list_focused, theme)

    is_exit_focused = (focus_mode == "top_bar" and button_selected == 4) or (
            view_mode == "button" and focus_mode == "games")
    draw_console_btn(screen, "EXIT", exit_rect, is_exit_focused, theme)

    draw_console_btn(screen, "+ ADD", add_rect, (focus_mode == "buttons" and button_selected == 0), theme)
    draw_console_btn(screen, "SEARCH", search_btn_rect, (focus_mode == "buttons" and button_selected == 5), theme)

    stxt = search_query + (
        "|" if focus_mode == "search" and time.time() % 1 > 0.5 else "") if search_query or focus_mode == "search" else "Search library..."
    screen.blit(font_main.render(stxt, True, theme["text"]), (search_btn_rect.right + 15, search_bar_rect.y + 10))


    # INPUT HANDLING
    mouse_pos = pygame.mouse.get_pos()
    clickable = [theme_rect, grid_rect, list_rect, exit_rect, add_rect, search_bar_rect]

    hovering_game = False
    if focus_mode == "games":
        if mouse_pos[1] > HEADER_H:
            hovering_game = True

    if any(rect.collidepoint(mouse_pos) for rect in clickable) or hovering_game:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    # --- JOYSTICK STICK CHECK (Outside event loop) ---
    current_time = pygame.time.get_ticks()
    if joysticks and current_time > joy_delay:
        joy = list(joysticks.values())[0]
        # Stick axes
        ax_x, ax_y = joy.get_axis(0), joy.get_axis(1)
        # D-Pad (Hats)
        hat_x, hat_y = 0, 0
        if joy.get_numhats() > 0:
            hat_x, hat_y = joy.get_hat(0)

        nav_key = None
        if ax_y < -0.5 or hat_y > 0.5:
            nav_key = pygame.K_UP
        elif ax_y > 0.5 or hat_y < -0.5:
            nav_key = pygame.K_DOWN
        elif ax_x < -0.5 or hat_x < -0.5:
            nav_key = pygame.K_LEFT
        elif ax_x > 0.5 or hat_x > 0.5:
            nav_key = pygame.K_RIGHT

        if nav_key:
            handle_navigation(nav_key, cols, len(filtered))
            joy_delay = current_time + 200

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_settings()
            draw_loading_screen("CLOSING PYCONSOLE...", 800, theme)
            fade_screen(W, H, direction='out', speed=10)
            running = False

        if event.type == pygame.JOYDEVICEADDED:
            joy = pygame.joystick.Joystick(event.device_index)
            joysticks[joy.get_instance_id()] = joy
            print(f"Controller {joy.get_name()} connected!")

        if event.type == pygame.JOYDEVICEREMOVED:
            del joysticks[event.instance_id]
            print("Controller disconnected!")

        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(
                (event.w, event.h),
                pygame.FULLSCREEN | pygame.SCALED | pygame.RESIZABLE
            )

        if event.type == pygame.MOUSEWHEEL:
            target_scroll_y -= event.y * 100

        # --- CONTROLLER BUTTON LOGIC ---
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:
                if focus_mode == "games":
                    if filtered and selected < len(filtered):
                        launch_game(filtered[selected], theme)

                elif focus_mode == "top_bar":
                    if button_selected == 1:
                        current_theme_idx = (current_theme_idx + 1) % len(THEMES)
                        save_settings()

                    elif button_selected == 2:
                        view_mode = "grid"
                        save_settings()

                    elif button_selected == 3:
                        view_mode = "list"
                        save_settings()

                    elif button_selected == 4:
                        save_settings()
                        draw_loading_screen("CLOSING PYCONSOLE...", 800, theme)
                        fade_screen(W, H, direction='out', speed=10)
                        running = False

                elif focus_mode == "buttons":
                    if button_selected == 0:
                        new_path = get_stable_directory()
                        if new_path:
                            LIBRARY_FOLDER = new_path
                            games = load_games(LIBRARY_FOLDER)
                            selected = 0
                            save_settings()

                    elif button_selected == 5:
                        focus_mode = "search"

            if event.button == 1:
                focus_mode = "games"

        # --- MOUSE CLICK LOGIC ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            m_pos = event.pos

            if theme_rect.collidepoint(m_pos):
                current_theme_idx = (current_theme_idx + 1) % len(THEMES)
                save_settings()

            if grid_rect.collidepoint(m_pos):
                view_mode = "grid"
                save_settings()

            if list_rect.collidepoint(m_pos):
                view_mode = "list"
                save_settings()

            if exit_rect.collidepoint(m_pos):
                save_settings()
                draw_loading_screen("CLOSING PYCONSOLE...", 800, theme)
                fade_screen(W, H, direction='out', speed=10)
                running = False

            if add_rect.collidepoint(m_pos):
                p = get_stable_directory()
                if p:
                    LIBRARY_FOLDER = p
                    games = load_games(p)
                    selected = 0
                    save_settings()

            if search_bar_rect.collidepoint(m_pos):
                focus_mode = "search"

            if focus_mode == "games":
                if filtered and selected < len(filtered):
                    launch_game(filtered[selected], theme)

        # --- MOUSE HOVER ---
        if event.type == pygame.MOUSEMOTION:
            m_pos = event.pos
            if theme_rect.collidepoint(m_pos):
                focus_mode, button_selected = "top_bar", 1
            elif grid_rect.collidepoint(m_pos):
                focus_mode, button_selected = "top_bar", 2
            elif list_rect.collidepoint(m_pos):
                focus_mode, button_selected = "top_bar", 3
            elif exit_rect.collidepoint(m_pos):
                focus_mode, button_selected = "top_bar", 4
            elif add_rect.collidepoint(m_pos):
                focus_mode, button_selected = "buttons", 0
            elif search_btn_rect.collidepoint(m_pos):
                focus_mode, button_selected = "buttons", 5

            if view_mode == "grid" and m_pos[1] > HEADER_H:
                focus_mode = "games"

        # --- KEYBOARD ---
        if event.type == pygame.KEYDOWN:
            if focus_mode == "search":
                if event.key == pygame.K_BACKSPACE:
                    search_query = search_query[:-1]
                elif event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    focus_mode = "games"
                else:
                    search_query += event.unicode
                    selected = 0

            elif focus_mode == "buttons":
                if event.key == pygame.K_UP:
                    focus_mode = "top_bar"
                    button_selected = 1

                elif event.key == pygame.K_DOWN:
                    focus_mode = "games"
                    selected = 0

                elif event.key == pygame.K_LEFT:
                    button_selected = 0 if button_selected == 5 else 5
                elif event.key == pygame.K_RIGHT:
                    button_selected = 5 if button_selected == 0 else 0

                elif event.key == pygame.K_RETURN:
                    if button_selected == 0:
                        p = get_stable_directory()
                        if p:
                            LIBRARY_FOLDER = p
                            games = load_games(p)
                            save_settings()

                    elif button_selected == 5:
                        focus_mode = "search"

            elif focus_mode == "top_bar":
                if event.key == pygame.K_DOWN:
                    focus_mode = "buttons"
                    button_selected = 0

                elif event.key == pygame.K_LEFT:
                    button_selected = max(1, button_selected - 1)
                elif event.key == pygame.K_RIGHT:
                    button_selected = min(4, button_selected + 1)

                elif event.key == pygame.K_RETURN:
                    if button_selected == 1:
                        current_theme_idx = (current_theme_idx + 1) % len(THEMES)
                        save_settings()

                    elif button_selected == 2:
                        view_mode = "grid"
                        save_settings()

                    elif button_selected == 3:
                        view_mode = "list"
                        save_settings()

                    elif button_selected == 4:
                        save_settings()
                        draw_loading_screen("CLOSING PYCONSOLE...", 800, theme)
                        fade_screen(W, H, direction='out', speed=10)
                        running = False

            elif focus_mode == "games":
                if event.key == pygame.K_UP:
                    if selected < cols:
                        focus_mode = "buttons"
                        button_selected = 0
                    else:
                        selected -= cols

                elif event.key == pygame.K_DOWN:
                    if selected + cols < len(filtered):
                        selected += cols

                elif event.key == pygame.K_LEFT:
                    selected = max(0, selected - 1)
                elif event.key == pygame.K_RIGHT:
                    selected = min(len(filtered) - 1, selected + 1)

                elif event.key == pygame.K_RETURN and filtered:
                    launch_game(filtered[selected], theme)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()