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


class GameManager:
    def __init__(self, library_folder: str):
        self.library_folder = library_folder
        self.games = self._load_games()
        self.pending_game = None

    # ------------------------------------------------------------------
    # Library
    # ------------------------------------------------------------------

    def _load_games(self) -> list[dict]:
        loaded = []
        if not os.path.exists(self.library_folder):
            return loaded

        for filename in os.listdir(self.library_folder):
            if filename.endswith((".pgame", ".pygame", ".pgp", ".pypkg")):
                p = os.path.join(self.library_folder, filename)
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

    def reload(self):
        self.games = self._load_games()

    def filter(self, query: str) -> list[dict]:
        return [g for g in self.games if query.lower() in g["name"].lower()]

    # ------------------------------------------------------------------
    # Launching
    # ------------------------------------------------------------------

    def select(self, game: dict):
        self.pending_game = game

    @property
    def has_pending(self) -> bool:
        return self.pending_game is not None

    def launch(self, screen, clock, font, theme, app_name) -> pygame.Surface:
        if not self.pending_game:
            print("No pending game!")
            return screen

        # print(f"Launching: {self.pending_game['path']}")

        W, H = screen.get_size()
        fade_screen(screen, W, H, direction="in", speed=10)
        fade_screen(screen, W, H, direction="out", speed=10)
        draw_loading_screen(
            screen,
            clock,
            font,
            theme,
            f"BOOTING {self.pending_game['name'].upper()}...",
        )

        temp_dir = tempfile.mkdtemp(prefix="pyconsole_run_")
        original_cwd = os.getcwd()
        original_path = sys.path.copy()

        try:
            with zipfile.ZipFile(self.pending_game["path"], "r") as z:
                z.extractall(temp_dir)
            # print(f"Extracted to {temp_dir}: {os.listdir(temp_dir)}")

            target_entry = self.pending_game.get("entry", "main.py")
            script_path = None
            for root, dirs, files in os.walk(temp_dir):
                if target_entry in files:
                    script_path = os.path.join(root, target_entry)
                    sys.path.insert(0, root)
                    os.chdir(root)
                    break
            # print(f"script_path = {script_path}")

            if script_path:
                spec = importlib.util.spec_from_file_location("game_run", script_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                # print(f"Module loaded. Has Game? {hasattr(module, 'Game')}, has create_game? {hasattr(module, 'create_game')}")

                if hasattr(module, "Game"):
                    module.Game(screen).run()
                elif hasattr(module, "create_game"):
                    module.create_game(screen)

        except Exception as e:
            print(f"Game Crash: {e}")
            import traceback
            traceback.print_exc()

        finally:
            try:
                if pygame.mixer.get_init():
                    pygame.mixer.music.stop()
            except Exception:
                pass

            if not pygame.display.get_init():
                pygame.display.init()
            if not pygame.font.get_init():
                pygame.font.init()

            screen = pygame.display.set_mode((W, H), pygame.SCALED)
            pygame.display.set_caption(app_name)
            pygame.event.clear()

            fade_screen(screen, W, H, direction="out", speed=10)
            draw_loading_screen(
                screen, clock, font, theme, f"RETURNING TO {app_name.upper()}..."
            )
            screen.fill(theme["bg"])
            pygame.display.flip()

        return screen
