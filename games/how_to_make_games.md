# Game Project Structure & Release (`.pyg`)

`.pyg` is the official game package format for **PyConsole**. Games are no longer released by zipping a folder and renaming the extension — they're built into a real binary package using the `pyg` CLI (`pygpack` on PyPI).

---

## 📁 Project Structure

Before building, your game just needs to exist as a normal folder on disk:

```
my_game/
├── meta.json
├── main.py
├── icon.png
└── assets/
    ├── sprites/
    ├── sounds/
    └── fonts/
```

There's no required folder layout beyond that — everything under `my_game/` gets packaged as-is, so organize `assets/` however makes sense for your game. The only two files with special meaning are `meta.json` (becomes the package's metadata, not a regular packaged file) and whatever your `entry` field points to.

### `meta.json`

```json
{
    "name": "My First Game",
    "id": "com.example.myfirstgame",
    "version": "1.0.0",
    "author": "Your Name",
    "entry": "main.py",
    "icon": "icon.png"
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `name` | ✅ | Display name shown in the console |
| `id` | ✅ | Unique, reverse-DNS style by convention (e.g. `com.you.gamename`) |
| `entry` | ✅ | Path to the entry Python file; must exist in the project after build |
| `version`, `author`, `icon`, ... | optional | Free-form — unknown keys are kept, not stripped |

### `main.py` (entry point)

Same contract as before — `create_game(screen)` is what the console runtime calls, and games should hand control back cleanly (`return "QUIT_TO_CONSOLE"`) instead of calling `sys.exit()`.

---

## 🚀 Releasing / Exporting a Game

Exporting is no longer "zip it, rename it." You build a real `.pyg` package with the `pyg` CLI.

### 1. Install the tool

```bash
pip install pygpack
```

### 2. Build

```bash
pyg build my_game/                   # writes my_game.pyg next to the project folder
pyg build my_game/ -o dist/game.pyg  # or choose an explicit output path
```

This reads `meta.json`, packages every other file in the folder, and produces a single binary `.pyg` file (the current **PYG1** format). Unlike the old zip-based approach, you can no longer just rename a `.pyg` to `.zip` and open it — the file is a proper binary container with its own header, metadata block, file table, and data region.

Optional: ship compiled bytecode instead of raw source —

```bash
pyg build my_game/ --compile   # packages .pyc instead of .py; meta.json's entry is updated automatically
```

This is casual source hiding (raises the bar past "open in a text editor"), not real protection — a determined person can still decompile it. Don't rely on it for anything sensitive.

### 3. Verify before shipping

```bash
pyg validate my_game.pyg   # runs full structural + checksum validation, pass/fail report
pyg info my_game.pyg       # prints the manifest
pyg list my_game.pyg       # lists every packaged file
```

Always run `pyg validate` before distributing — it checks header integrity, file table consistency, path safety, and per-file checksums in one pass.

### 4. Test it runs

```bash
pyg run my_game.pyg
```

This extracts the package to a temporary runtime directory, launches your entry point with `cwd` set there (so relative asset paths like `assets/player.png` resolve exactly like they would unpackaged), and cleans up afterward. Use `--keep-temp` if you need to inspect the extracted files while debugging.

### 5. Distribute

Move the resulting `.pyg` file into:

```
/games/
```

The console will detect and list it automatically — same as before, just with a real package format underneath instead of a renamed zip.

---

## Summary of the workflow

```
my_game/ (source folder)
      │
      │  pyg build my_game/
      ▼
my_game.pyg (single binary package)
      │
      │  pyg validate → pyg run (test)
      ▼
copy into /games/
```