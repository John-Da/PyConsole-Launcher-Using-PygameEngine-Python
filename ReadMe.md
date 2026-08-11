<img width="2760" height="1160" alt="pyconsole_logo" src="https://github.com/user-attachments/assets/f5e122ec-4f28-4ea4-84b9-95f6140116f8" />

# 🕹️ Pygame Console

A custom console firmware built with Python and Pygame, designed to provide a unified, controller-friendly gaming environment with its own system interface, game library, settings, and runtime.

Inspired by modern handheld consoles such as the Steam Deck and PSP/PS Vita, as well as classic retro gaming systems, **Pygame Console** explores how Python and Pygame can be used to build a complete console-oriented software experience.

![Static Badge](https://img.shields.io/badge/python-v3.12.6-blue?logo=python)
![Static Badge](https://img.shields.io/badge/pygame-v2.6.0-green?logo=pygame)

---

## 🧠 Core Concept

Pygame Console is designed as a **console-style software environment**, rather than simply a launcher for individual Pygame projects.

The firmware provides the system-level experience around games, including navigation, game management, settings, input handling, visual transitions, and runtime management.

Games are packaged and launched through the Pygame Console runtime, allowing individual Pygame projects to operate within a consistent console environment.

**Architecture:**

```text
Game Package
      ↓
Pygame Console Runtime
      ↓
Console Firmware
      ↓
Hardware
```

### Core Features

* Boot animation and system startup
* Console-style home interface
* Game library with grid/list views
* Game metadata system (icon, description, version, author)
* Controller and keyboard input abstraction
* GPIO button input support
* JSON-based settings management
* UI transitions and visual effects
* Packaged game support (`.pyg`, ZIP-based packages)
* Managed game runtime and launching

---

## 📦 Game Packaging

Pygame Console supports packaged games that can be installed into the console's game library.

Each game package can contain its own:

* Entry point
* Game assets
* Screens and modules
* Metadata
* Icon
* Dependencies required by the game

> **📖 Note:** Want to learn how to package and release games for Pygame Console?
> See the [Game Packaging Guide](https://github.com/John-Da/PyConsole-Launcher-Using-PygameEngine-Python/blob/main/games/how_to_make_games.md) for more information.


### Example Package

```text
Neon Striker.pyg
│
├── main.py
├── meta.json
├── screens/
│   ├── __init__.py
│   ├── game_intro.py
│   └── ...
├── assets/
└── ...
```

The console extracts and runs each package inside its own temporary runtime environment, allowing games to maintain their own internal structure while remaining integrated with the console interface.

---

## 🚧 Development Status

### ✅ Implemented

* Boot animation
* Home UI
* Navigation system
* Game library
* Game metadata
* Basic game launching
* Game package loading
* Settings save/load
* Power options
* Shutdown flow
* Controller/input handling
* Improved focus and navigation logic

### 🔄 In Progress

* Expanded controller support
* Runtime and package improvements
* Performance optimization
* Additional system features

---

## 📸 Screenshots

|                                                 Startup                                                 |                                                  Games                                                  |                                                Game Info                                                |                                                  Store                                                  |
| :-----------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------: |
| <img src="https://github.com/user-attachments/assets/deb66d95-c9f8-49e7-8e55-1c0d76c9fffe" width="200"> | <img src="https://github.com/user-attachments/assets/aa1157be-9b25-47fc-a89b-09d6044447ec" width="200"> | <img src="https://github.com/user-attachments/assets/bad8015f-5809-4595-8f94-f924dbf3dc3f" width="200"> | <img src="https://github.com/user-attachments/assets/9612ba7c-cec1-4abd-9c68-9ec9e24fd825" width="200"> |

|                                                 Settings                                                |                                              Power Options                                              |                                                 Shutdown                                                |
| :-----------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------: |
| <img src="https://github.com/user-attachments/assets/10d575e0-2f33-48c7-bd07-fba94c1c06ea" width="200"> | <img src="https://github.com/user-attachments/assets/21504f22-7bd4-4d2e-b206-11e89dd0bb18" width="200"> | <img src="https://github.com/user-attachments/assets/84c22510-6ddc-4bca-be02-37e8a517fb99" width="200"> |

---

## 🧰 Built With

* [Python](https://python.org) (v3.12.6)
* [Pygame](https://pygame.org) (v2.6.0)

## 📝 Credits

* Free Music & SFX — [Pixabay](https://pixabay.com)
* Sample games — original works by the author

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/John-Da/PyConsole-Launcher-Using-PygameEngine-Python/blob/main/LICENSE) file for details.
