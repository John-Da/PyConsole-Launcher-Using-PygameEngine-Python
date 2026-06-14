import pygame
import os
import sys
import json
import zipfile
import io
import tempfile
import shutil
import importlib.util

from ui.components import fade_screen, draw_loading_screen


def load_games(path: str) -> list[dict]:
    """
    Scans `path` for .pgame/.pygame/.pgp/.pypkg archives and returns a list
    of game metadata dicts: name, author, version, entry, path, icon, size.

    Metadata is read from meta.json inside each archive if present;
    falls back to filename-derived defaults otherwise.
    """
    loaded = []
    if not os.path.exists(path):
        return loaded

    for filename in os.listdir(path):
        if filename.endswith((".pgame", ".pygame", ".pgp", ".pypkg")):
            p = os.path.join(path, filename)
            game_icon = None
            meta = {
                "title": filename[:-7].replace("_", " "),
                "author": "Unknown",
                "version": "1.0",
                "entry": "main.py",
            }
            try:
                with zipfile.ZipFile(p, "r") as z:
                    file_list = z.namelist()
                    meta_p = next(
                        (f for f in file_list if f.endswith("meta.json")), None
                    )
                    icon_p = next(
                        (f for f in file_list if f.endswith("icon.png")), None
                    )

                    if meta_p:
                        with z.open(meta_p) as f:
                            meta.update(json.load(f))

                    if icon_p:
                        with z.open(icon_p) as f:
                            game_icon = pygame.image.load(
                                io.BytesIO(f.read())
                            ).convert_alpha()
            except Exception:
                pass

            loaded.append(
                {
                    "name": meta["title"],
                    "author": meta["author"],
                    "version": meta["version"],
                    "entry": meta["entry"],
                    "genre": meta.get("genre"),
                    "description": meta.get("description"),
                    "path": p,
                    "icon": game_icon,
                    "size": f"{os.path.getsize(p) / (1024 * 1024):.1f} MB",
                }
            )

    return loaded


def launch_game(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    font_main,
    game_data: dict,
    theme: dict,
    app_name: str,
) -> pygame.Surface:
    """
    Extracts and runs a .pgame archive's entry script, then restores the
    display and returns the (possibly recreated) screen surface.

    The game can define either:
      - a `Game` class with a `__init__(self, screen)` and `run(self)` method, or
      - a `create_game(screen)` function.

    Returns the screen surface to use going forward (display is torn down
    and recreated after the game exits, so the caller must reassign their
    `screen` variable to this return value).
    """
    W, H = screen.get_size()
    fade_screen(screen, W, H, direction="in", speed=10)
    fade_screen(screen, W, H, direction="out", speed=10)
    draw_loading_screen(
        screen, clock, font_main, theme, f"BOOTING {game_data['name'].upper()}..."
    )

    temp_dir = tempfile.mkdtemp(prefix="pyconsole_run_")
    original_cwd = os.getcwd()
    original_path = sys.path.copy()

    try:
        with zipfile.ZipFile(game_data["path"], "r") as z:
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

            if hasattr(module, "Game"):
                game_instance = module.Game(screen)
                game_instance.run()
            elif hasattr(module, "create_game"):
                module.create_game(screen)

    except Exception as e:
        print(f"Game Crash: {e}")

    finally:
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except Exception:
            pass

        fade_screen(screen, W, H, direction="out", speed=10)
        draw_loading_screen(
            screen, clock, font_main, theme, f"RETURNING TO {app_name.upper()}..."
        )

        os.chdir(original_cwd)
        sys.path = original_path
        shutil.rmtree(temp_dir, ignore_errors=True)

        pygame.display.quit()
        pygame.display.init()
        pygame.font.init()

        screen = pygame.display.set_mode((W, H), pygame.SCALED)
        pygame.display.set_caption(app_name)
        pygame.event.clear()

        screen.fill(theme["bg"])
        pygame.display.flip()

    return screen
