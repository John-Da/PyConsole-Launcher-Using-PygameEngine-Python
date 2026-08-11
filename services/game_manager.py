import pygame
import os
import sys
import json
import zipfile
import io
import tempfile
import shutil
import importlib
import importlib.util
from ui.components import fade_screen, draw_loading_screen

# .pyg files can be either the new PYG1 binary container format or the
# older ZIP-based format (renamed .zip -> .pyg). PYG1 files always start
# with this 4-byte magic number; anything else ending in one of the
# recognized extensions is assumed to be a ZIP archive, same as before.
PYG1_MAGIC = b"PYG1"

# Extensions pygame can actually load. .icns and .ico are deliberately
# excluded -- SDL_image doesn't support either, and both show up often
# enough in real icons/ folders (macOS .icns, Windows .ico variants
# sitting next to the .png) to cause silent blank icons or crashes if
# picked up.
VALID_ICON_EXTS = (".png", ".jpg", ".jpeg", ".bmp")


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
            if filename.endswith((".pyg")):
                p = os.path.join(self.library_folder, filename)
                if self._is_pyg1(p):
                    game = self._load_game_pyg(p, filename)
                else:
                    game = self._load_game_zip(p, filename)
                if game:
                    loaded.append(game)
        return loaded

    @staticmethod
    def _is_pyg1(path: str) -> bool:
        try:
            with open(path, "rb") as f:
                return f.read(len(PYG1_MAGIC)) == PYG1_MAGIC
        except OSError:
            return False

    @staticmethod
    def _default_meta(filename: str) -> dict:
        title = os.path.splitext(filename)[0].replace("_", " ")
        return {
            "title": title,
            "author": "Unknown",
            "version": "1.0",
            "entry": "main.py",
        }

    @staticmethod
    def _pick_best_icon(
        file_list: list[str], preferred_name: str | None = None
    ) -> str | None:
        """Pick the best icon path out of a package's file list.

        Tries, in order:
          1. `preferred_name` (usually meta.json's "icon" field), if it's
             present in the package and has a pygame-loadable extension.
          2. An exact "icon.<ext>" at the package root, preferring .png.
          3. Any pygame-loadable image under an "icons/" folder (this is
             the case that was previously missed entirely -- projects
             that keep icon.png/icon.icns/icon.ico variants together in
             an icons/ subfolder instead of a single root-level file).
          4. Any file anywhere in the package whose name starts with
             "icon" and has a loadable extension.

        Never returns a .icns/.ico/etc. path, and never returns a
        directory -- only exact, loadable image file paths.
        """

        def is_valid_image(name: str) -> bool:
            return name.lower().endswith(VALID_ICON_EXTS)

        def prefer_png(name: str) -> int:
            return 0 if name.lower().endswith(".png") else 1

        if (
            preferred_name
            and preferred_name in file_list
            and is_valid_image(preferred_name)
        ):
            return preferred_name

        root_candidates = sorted(
            (
                f
                for f in file_list
                if "/" not in f
                and os.path.splitext(f)[0].lower() == "icon"
                and is_valid_image(f)
            ),
            key=prefer_png,
        )
        if root_candidates:
            return root_candidates[0]

        icons_folder_candidates = sorted(
            (
                f
                for f in file_list
                if is_valid_image(f)
                and f.replace("\\", "/").split("/")[:-1][-1:] == ["icons"]
            ),
            key=lambda f: (
                0 if os.path.splitext(f)[0].lower() == "icon" else 1,
                prefer_png(f),
            ),
        )
        if icons_folder_candidates:
            return icons_folder_candidates[0]

        anywhere_candidates = sorted(
            (
                f
                for f in file_list
                if is_valid_image(f) and os.path.basename(f).lower().startswith("icon")
            ),
            key=prefer_png,
        )
        if anywhere_candidates:
            return anywhere_candidates[0]

        return None

    def _load_game_zip(self, p: str, filename: str) -> dict:
        """Legacy ZIP-based .pgame/.pygame/.pgp/.pypkg/.pyg files."""
        game_icon = None
        meta = self._default_meta(filename)
        try:
            with zipfile.ZipFile(p, "r") as z:
                file_list = z.namelist()
                meta_p = next((f for f in file_list if f.endswith("meta.json")), None)
                if meta_p:
                    with z.open(meta_p) as f:
                        loaded_meta = json.load(f)
                    # manifest.json/meta.json declare the title under
                    # "name" (per the packaging docs), but the internal
                    # dict here has always used "title" -- meta.update()
                    # alone just added a second, unread "name" key rather
                    # than overwriting "title", so a game's real declared
                    # name was silently ignored in favor of the
                    # filename-derived default. Map it across explicitly.
                    if "name" in loaded_meta and "title" not in loaded_meta:
                        loaded_meta["title"] = loaded_meta["name"]
                    meta.update(loaded_meta)

                icon_p = self._pick_best_icon(file_list, meta.get("icon"))
                if icon_p:
                    with z.open(icon_p) as f:
                        game_icon = pygame.image.load(
                            io.BytesIO(f.read())
                        ).convert_alpha()
        except Exception as e:
            print(f"Warning: couldn't read {filename} as a ZIP-based package: {e}")
        return self._make_entry(p, meta, game_icon)

    def _load_game_pyg(self, p: str, filename: str) -> dict:
        """New PYG1 binary container .pyg files, via the `pyg` package
        (pip install pygpack)."""
        meta = self._default_meta(filename)
        game_icon = None
        try:
            from pyg.format.reader import Pyg1Package
        except ImportError:
            print(
                f"Skipping {filename}: this is a PYG1 package, which needs "
                "`pip install pygpack` to read. ZIP-based .pyg/.pgame/etc. "
                "files still work without it."
            )
            return None

        try:
            with Pyg1Package(p) as pkg:
                manifest = pkg.read_metadata()
                meta.update(
                    {
                        "title": manifest.get("name", meta["title"]),
                        "author": manifest.get("author", meta["author"]),
                        "version": manifest.get("version", meta["version"]),
                        "entry": manifest.get("entry", meta["entry"]),
                        "genre": manifest.get("genre"),
                        "description": manifest.get("description"),
                    }
                )
                icon_name = self._pick_best_icon(pkg.list_files(), manifest.get("icon"))
                if icon_name:
                    game_icon = pygame.image.load(
                        io.BytesIO(pkg.read(icon_name))
                    ).convert_alpha()
        except Exception as e:
            print(f"Warning: couldn't read {filename} as a PYG1 package: {e}")
        return self._make_entry(p, meta, game_icon)

    @staticmethod
    def _make_entry(p: str, meta: dict, game_icon) -> dict:
        return {
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

    def reload(self):
        self.games = self._load_games()

    def filter(self, query: str) -> list[dict]:
        return [g for g in self.games if query.lower() in g["name"].lower()]

    def set_library_folder(self, folder):
        self.library_folder = folder
        self.games = self._load_games()

    # ------------------------------------------------------------------
    # Launching
    # ------------------------------------------------------------------
    def select(self, game: dict):
        self.pending_game = game

    @property
    def has_pending(self) -> bool:
        return self.pending_game is not None

    def _extract_game(self, game_path: str, temp_dir: str) -> None:
        """Extract a game package to temp_dir, using whichever format it is."""
        if self._is_pyg1(game_path):
            from pyg.format.reader import Pyg1Package

            with Pyg1Package(game_path) as pkg:
                pkg.extract_all(temp_dir)
        else:
            with zipfile.ZipFile(game_path, "r") as z:
                z.extractall(temp_dir)

    def launch(self, screen, clock, font, theme, app_name) -> pygame.Surface:
        if not self.pending_game:
            return screen
        
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
            self._extract_game(self.pending_game["path"], temp_dir)

            target_entry = self.pending_game.get("entry", "main.py")
            script_path = None
            game_root = None

            for root, dirs, files in os.walk(temp_dir):
                if target_entry in files:
                    script_path = os.path.join(root, target_entry)
                    game_root = root

                    # Add the game's root directory to Python's import path
                    sys.path.insert(0, game_root)

                    # Make the game's directory the current working directory
                    os.chdir(game_root)

                    # Make Python refresh its package/module cache
                    importlib.invalidate_caches()

                    break

            if script_path:
                # --------------------------------------------------------------
                # Prepare isolated game imports
                # --------------------------------------------------------------

                # Remove possible PyConsole modules that have the same names
                # as modules inside the game package.
                game_modules = [
                    name
                    for name in list(sys.modules)
                    if name == "screens" or name.startswith("screens.")
                ]

                for name in game_modules:
                    del sys.modules[name]

                # Make sure Python searches the extracted game first.
                sys.path.insert(0, game_root)

                # Refresh import caches after extracting the game.
                importlib.invalidate_caches()

                # --------------------------------------------------------------
                # Load main.py
                # --------------------------------------------------------------

                spec = importlib.util.spec_from_file_location(
                    "game_run",
                    script_path,
                )

                if spec is None or spec.loader is None:
                    raise ImportError(
                        f"Could not load game entry point: {script_path}"
                    )

                module = importlib.util.module_from_spec(spec)

                # Register the game module.
                sys.modules["game_run"] = module

                # Execute main.py.
                spec.loader.exec_module(module)

                # --------------------------------------------------------------
                # Start the game
                # --------------------------------------------------------------

                if hasattr(module, "Game"):
                    module.Game(screen).run()

                elif hasattr(module, "create_game"):
                    module.create_game(screen)

                else:
                    print(
                        "Game loaded, but no Game class or "
                        "create_game() function was found."
                    )

        except Exception as e:
            print(f"Game Crash: {e}")
            import traceback

            traceback.print_exc()

        finally:
            # Restore the console's own working directory and import path --
            # previously left pointed inside the (soon-to-be-deleted) temp
            # dir, which would break every subsequent game launch's relative
            # paths and leak an extra sys.path entry per game played.
            # Previously never cleaned up -- every launch permanently left
            # behind a pyconsole_run_* temp directory.
            # Remove dynamically loaded game modules
            os.chdir(original_cwd)
            sys.path[:] = original_path
            sys.modules.pop("game_run", None)

            # Remove game-local modules
            for name in list(sys.modules):
                if name == "screens" or name.startswith("screens."):
                    del sys.modules[name]

            shutil.rmtree(temp_dir, ignore_errors=True)

            try:
                if pygame.mixer.get_init():
                    pygame.mixer.music.stop()
            except Exception:
                pass
            if not pygame.display.get_init():
                pygame.display.init()
            if not pygame.font.get_init():
                pygame.font.init()
            screen = pygame.display.set_mode((W, H))
            # screen = pygame.display.set_mode((W, H), pygame.SCALED | pygame.FULLSCREEN)
            pygame.display.set_caption(app_name)
            pygame.event.clear()
            fade_screen(screen, W, H, direction="out", speed=10)
            draw_loading_screen(
                screen, clock, font, theme, f"RETURNING TO {app_name.upper()}..."
            )
            screen.fill(theme["bg"])
            pygame.display.flip()
        return screen
