<img width="2760" height="1160" alt="pyconsole_logo" src="https://github.com/user-attachments/assets/f5e122ec-4f28-4ea4-84b9-95f6140116f8" />


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

| Startup | Games | Game Info | Store |
| :---: | :---: | :---: | :---: |
| <img src="https://github.com/user-attachments/assets/deb66d95-c9f8-49e7-8e55-1c0d76c9fffe" width="200"> | <img src="https://github.com/user-attachments/assets/aa1157be-9b25-47fc-a89b-09d6044447ec" width="200"> | <img src="https://github.com/user-attachments/assets/bad8015f-5809-4595-8f94-f924dbf3dc3f" width="200"> | <img src="https://github.com/user-attachments/assets/9612ba7c-cec1-4abd-9c68-9ec9e24fd825" width="200"> |

| Settings | Power Options | Shutdown |
| :---: | :---: | :---: |
| <img src="https://github.com/user-attachments/assets/10d575e0-2f33-48c7-bd07-fba94c1c06ea" width="200"> | <img src="https://github.com/user-attachments/assets/21504f22-7bd4-4d2e-b206-11e89dd0bb18" width="200"> | <img src="https://github.com/user-attachments/assets/84c22510-6ddc-4bca-be02-37e8a517fb99" width="200"> |

## 🧰 Built With

- [Python](https://python.org) (v3.12.6)
- [Pygame](https://pygame.org) (v2.6.0)

## 📝 Credits

- Free Music & SFX — [Pixabay](https://pixabay.com)
- Sample games — original works by the author



