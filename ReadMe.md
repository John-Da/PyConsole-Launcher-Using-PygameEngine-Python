# 🕹️ Pygame Console APP

A console OS runtime built entirely with Python and Pygame — inspired by the Steam Deck, PSP/PS Vita, and classic retro consoles.

Pygame has always been powerful but fragmented. Most projects are distributed as standalone apps with no unified launcher, system UI, or controller-friendly experience. **Pygame Console APP** changes that by wrapping pygame games in a managed, console-style environment.

![Static Badge](https://img.shields.io/badge/python-v3.12.6-blue?logo=python)
![Static Badge](https://img.shields.io/badge/pygame-v2.6.0-green?logo=pygame)

---

## 🧠 Core Concept

Instead of running pygame games directly, each game runs *inside* the Pygame Console APP environment.

The system provides:

- Boot animation
- Game library grid/list view
- Game metadata system (icon, description, version, author)
- Input abstraction layer (keyboard, controller, GPIO buttons)
- Settings manager (JSON-based)
- Smooth transitions and UI effects
- Game packaging support (e.g. zip loading)

**Architecture:**
```bash
Your Game → Pygame Console Runtime → Hardware
```

---

### ✅ Implemented
- Boot animation
- Home UI
- Navigation system
- Basic game launching
- Settings save/load

### 🔄 In Progress
- Improved focus logic
- Better controller handling
- Performance optimization for Pi Zero 2 W / Pi 5

---

## 📸 Screenshots

| A | B | C | D |
| :-: | :-: | :-: | :-: |
| Start Up <img src="https://github.com/John-Da/PyConsole-Launcher-Using-PygameEngine-Python/raw/main/demos/startup.png" width="200"/> | GameBoy Theme <img src="https://github.com/John-Da/PyConsole-Launcher-Using-PygameEngine-Python/raw/main/demos/gb-theme.png" width="200"/> | Switch Theme <img src="https://github.com/John-Da/PyConsole-Launcher-Using-PygameEngine-Python/raw/main/demos/switch-theme.png" width="200"/> | Kawaii Theme <img src="https://github.com/John-Da/PyConsole-Launcher-Using-PygameEngine-Python/raw/main/demos/kawaii-theme.png" width="200"/> |
| 3DS White <img src="https://github.com/John-Da/PyConsole-Launcher-Using-PygameEngine-Python/raw/main/demos/3ds-white-theme.png" width="200"/> | Midnight Theme <img src="https://github.com/John-Da/PyConsole-Launcher-Using-PygameEngine-Python/raw/main/demos/midnigh-theme.png" width="200"/> | Shutdown <img src="https://github.com/John-Da/PyConsole-Launcher-Using-PygameEngine-Python/raw/main/demos/shutdown.png" width="200"/> |  |


https://github.com/user-attachments/assets/eaebc412-ea0c-4849-ba60-136d7c23a293


## 🧰 Built With

- [Python](https://python.org) (v3.12.6)
- [Pygame](https://pygame.org) (v2.6.0)

## 📝 Credits

- Free Music & SFX — [Pixabay](https://pixabay.com)
- Sample games — original works by the author



