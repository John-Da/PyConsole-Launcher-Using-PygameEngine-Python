# How to Make Games (`.pgame`)

`.pgame` is the official game package format for **Pygame Console APP**.
It is designed to standardize how games are structured, discovered, launched, and managed inside the console runtime.

Instead of running raw Python scripts, games are wrapped into a `.pgame` package that contains:

- Game source code
- Assets (images, audio, fonts)
- Metadata
- Entry configuration

This ensures every game follows the same structure and works seamlessly with the console.

---

## 📦 What is a `.pgame` File?

A `.pgame` file is simply a structured zip package with a custom extension.
Internally, it contains:

```
my_game.pgame
│
├── main.py
├── manifest.json
├── icon.png
├── /assets
│   ├── sprites/
│   ├── sounds/
│   └── fonts/
```

> You can rename `.pgame` to `.zip` to inspect its contents.

---

## 📄 Required Files

### 1️⃣ `main.py`

This is the entry point of your game.

**Requirements:**
- Must contain a `create_game()` function
- Must return control back to console properly when exiting
- Should not call `sys.exit()` directly

**Example:**

```python
def create_game(screen):
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        pygame.display.flip()
        clock.tick(60)
```

The console runtime will import and execute this function.

---

### 2️⃣ `manifest.json`

This file defines game metadata used by the console.

**Example:**

```json
{
    "name": "My First Game",
    "author": "Your Name",
    "version": "1.0.0",
    "description": "A simple demo game for Pygame Console.",
    "entry": "main.py",
    "icon": "icon.png"
}
```

**Required Fields:**

| Field | Description |
|-------|-------------|
| `name` | Display name in console |
| `author` | Developer name |
| `version` | Game version |
| `entry` | Entry Python file |
| `icon` | Thumbnail shown in library |

---

## 🎮 Game API (Console Runtime Integration)

When your game runs, it receives:

```python
create_game(screen)
```

Where:
- `screen` → The main pygame surface managed by console

This ensures:
- Resolution consistency
- Performance control
- Proper return to home screen

---

## 🔄 Exiting the Game Properly

To exit back to console:

```python
running = False
return "QUIT_TO_CONSOLE"
```

**Do NOT use:**

```python
sys.exit()
pygame.quit()
```

> The console manages the pygame lifecycle globally.

---

## 🖼 Icon Guidelines

- Recommended size: **256x256 px**
- Format: **PNG**
- Transparent background supported
- Keep design clean and readable

The icon will be shown in:
- Grid layout
- List layout
- Game details view

---

## 📁 Development Workflow

### Step 1 — Create Game Folder

```
my_game/
    main.py
    manifest.json
    icon.png
    assets/
```

### Step 2 — Test in Development Mode

You can run:

```bash
python main.py
```

Or test inside the console runtime.

### Step 3 — Package to `.pgame`

Compress the folder as zip:

```bash
zip -r my_game.zip my_game/
```

Rename:

```
my_game.zip → my_game.pgame
```

Move it into:

```
/games/
```

> The console will automatically detect it.

---

## 🧠 Advanced Features (Planned)

Future `.pgame` capabilities may include:

- Save data folder isolation
- Permission system
- Achievement hooks
- Network API access
- Sandboxed execution
- Plugin integration
- Performance profiling

---

## 🛡 Security Considerations (Planned)

In future versions:

- Games may run in a restricted execution environment
- Limited system access
- Safe error handling
- Crash isolation

---

## 🎯 Design Philosophy

`.pgame` exists to:

- Standardize pygame game structure
- Make installation simple (drag & drop)
- Create a console-like ecosystem
- Encourage cleaner architecture
- Prepare pygame for embedded handheld systems

> It transforms pygame from "just scripts" into a platform-ready game format.