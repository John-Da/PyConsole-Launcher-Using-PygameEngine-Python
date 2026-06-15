import pygame
import sys
import os
import json
import subprocess
import tkinter as tk
from tkinter import filedialog

def resource_path(*paths):
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base, *paths)

def get_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def terminate():
    pygame.quit()
    sys.exit()


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


def load_app_metadata(metadata_path):
    try:
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        name = metadata["name"]
        version = metadata["version"]
        author = metadata["author"]
        description = metadata["description"]

        return name, version, author, description

    except FileNotFoundError:
        print("metadata.json not found...")
        return "PyConsole", "v1.0.4", "John", ""


def save_settings(
    settings_file,
    LIBRARY_FOLDER,
    current_theme_idx,
    view_mode,
    performance_profile="Balanced",
    render_quality="medium",
):
    os.makedirs(os.path.dirname(settings_file), exist_ok=True)

    config = {
        "library_path": LIBRARY_FOLDER,
        "theme_index": current_theme_idx,
        "view_mode": view_mode,
        "performance_profile": performance_profile,
        "render_quality": render_quality,
    }
    with open(settings_file, "w") as f:
        json.dump(config, f, indent=4)


def load_settings(
    settings_file,
    LIBRARY_FOLDER,
    current_theme_idx,
    view_mode,
    performance_profile="Balanced",
    render_quality="medium",
):
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r") as f:
                config = json.load(f)

            LIBRARY_FOLDER = config.get("library_path", LIBRARY_FOLDER)
            current_theme_idx = config.get("theme_index", current_theme_idx)
            view_mode = config.get("view_mode", view_mode)
            performance_profile = config.get("performance_profile", performance_profile)
            render_quality = config.get("render_quality", render_quality)

        except:
            print("Settings file corrupted, using defaults.")

    return (
        LIBRARY_FOLDER,
        current_theme_idx,
        view_mode,
        performance_profile,
        render_quality,
    )


def handle_navigation(focus_mode, button_selected, selected, action, cols, total_games):

    if focus_mode == "buttons":
        if action == "UP":
            focus_mode, button_selected = "top_bar", 1
        elif action == "DOWN":
            focus_mode, selected = "games", 0
        elif action == "LEFT":
            button_selected = 5 if button_selected == 0 else 0
        elif action == "RIGHT":
            button_selected = 0 if button_selected == 5 else 5

    elif focus_mode == "top_bar":
        if action == "DOWN":
            focus_mode, button_selected = "buttons", 0
        elif action == "LEFT":
            button_selected = max(1, button_selected - 1)
        elif action == "RIGHT":
            button_selected = min(4, button_selected + 1)

    elif focus_mode == "games":
        if action == "UP":
            if selected < cols:
                focus_mode, button_selected = "buttons", 0
            else:
                selected -= cols
        elif action == "DOWN":
            if selected + cols < total_games:
                selected += cols
        elif action == "LEFT":
            selected = max(0, selected - 1)
        elif action == "RIGHT":
            selected = min(total_games - 1, selected + 1)

    return focus_mode, button_selected, selected
