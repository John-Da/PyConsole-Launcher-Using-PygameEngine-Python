# How to Make the Game — Project Structure & Release

This guide covers two things: how a game project should be structured, and
how to release it as a `.pyg` package for the console.

---

## 📁 Project Structure

```
my_game/
├── main.py
├── meta.json
├── icon.png            # OR use an icons/ folder instead — see below
└── assets/
    ├── sprites/
    ├── sounds/
    └── fonts/
```

- **`main.py`** — entry point. Must define `create_game(screen)`. Unrelated
  to packaging — this doesn't change based on how the game is released.
- **`meta.json`** — required. See schema below.
- **`icon.png`** (or an `icons/` folder — see [Icon Placement](#icon-placement)) — shown in the console's grid/list/details views.
- **`assets/`** — anything else your game needs: images, audio, fonts. Any
  folder structure underneath is preserved as-is when packaged.

---

## 📄 `meta.json`

```json
{
  "format": "pyg",
  "format_version": 1,
  "name": "Neon Striker",
  "id": "com.example.neonstriker",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "A fast-paced arcade shooter.",
  "entry": "main.py",
  "icon": "icon.png"
}
```

| Field | Required? | Description |
|---|---|---|
| `name` | **Yes** | Display name shown in the console |
| `id` | **Yes** | Unique identifier, reverse-DNS style (e.g. `com.you.gamename`) |
| `entry` | **Yes** | Entry Python file — must match your actual `main.py` (or whatever you name it) |
| `format` | No | Defaults to `"pyg"` automatically if omitted |
| `format_version` | No | Defaults to `1` automatically if omitted |
| `version` | No | Your game's version string |
| `author` | No | Developer/team name |
| `description` | No | Shown in the game details view |
| `icon` | No | Path to your icon file, if you're not relying on auto-detection (see below) |
| `genre` | No | Shown in the game details view, if your console UI displays it |

Unknown/extra fields beyond this list are preserved, not rejected — safe to
add your own if a future feature needs one.

---

## Icon Placement

Two layouts are both fully supported — pick whichever fits your project:

**Option A — single file at the project root:**
```
my_game/
├── icon.png
```

**Option B — an `icons/` folder**, useful if you keep multiple format
variants together (e.g. a `.icns` for a Mac build elsewhere, alongside the
`.png` the console actually uses):
```
my_game/
├── icons/
│   ├── icon.png
│   ├── icon.icns
│   └── icon.ico
```

The console automatically finds a usable icon in either location — you
don't need to point `meta.json`'s `"icon"` field at it explicitly unless
you want to override the auto-detected choice with a specific path.

**Format requirements:** `.png`, `.jpg`/`.jpeg`, or `.bmp` only.
`.icns`, `.ico`, `.svg`, and `.psd` are **not supported** — they're
automatically skipped during detection rather than causing a crash, but a
game that provides *only* one of these as its icon will show a blank
placeholder instead of the real artwork. Recommended size: 256×256 px, PNG
with transparency supported.

---

## 🚀 Releasing the Game

### 1. Install the build tool (one-time)

```bash
pip install pygpack
```

### 2. Build

```bash
pyg build my_game/
```

Produces `my_game.pyg` next to the `my_game/` folder — a single binary file
containing everything from the structure above.

Optional: ship compiled bytecode instead of readable `.py` source —

```bash
pyg build my_game/ --compile
```

### 3. Verify before shipping

```bash
pyg validate my_game.pyg   # package is well-formed
pyg list my_game.pyg       # everything got packaged
pyg info my_game.pyg       # metadata reads back correctly
pyg run my_game.pyg        # actually launches, same as the console will
```

### 4. Distribute

Move `my_game.pyg` into the console's `/games/` folder. It's auto-detected
— no extraction, no manual setup.

That single `.pyg` file is the whole release artifact — nothing else needs
to accompany it.
