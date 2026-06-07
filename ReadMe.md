# 🕹️ Pygame Console APP

A console OS runtime built entirely with Python and Pygame — inspired by the Steam Deck, PSP/PS Vita, and classic retro consoles.

Pygame has always been powerful but fragmented. Most projects are distributed as standalone apps with no unified launcher, system UI, or controller-friendly experience. **Pygame Console APP** changes that by wrapping pygame games in a managed, console-style environment.

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
| Start Up <img src="https://github.com/John-Da/PyConsole-Launcher-Using-PygameEngine-Python/blob/main/demos/startup.png" width="200"/> | GameBoy Theme <img src="https://github.com/John-Da/PyConsole-Launcher-Using-PygameEngine-Python/blob/main/demos/gb-theme.png" width="200"/> | Switch Theme <img src="https://github.com/John-Da/PyConsole-Launcher-Using-PygameEngine-Python/blob/main/demos/switch-theme.png" width="200"/> | Kawaii Theme <img src="https://github.com/John-Da/PyConsole-Launcher-Using-PygameEngine-Python/blob/main/demos/kawaii-theme.png" width="200"/> |
| 3DS White <img src="https://github.com/John-Da/PyConsole-Launcher-Using-PygameEngine-Python/blob/main/demos/3ds-white-theme.png" width="200"/> | Midnight Theme <img src="https://github.com/John-Da/PyConsole-Launcher-Using-PygameEngine-Python/blob/main/demos/midnigh-theme.png" width="200"/> | Shutdown <img src="https://github.com/John-Da/PyConsole-Launcher-Using-PygameEngine-Python/blob/main/demos/shutdown.png" width="200"/> |  |



