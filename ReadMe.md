# Pygame Console APP

Pygame Console APP is an operating system–like runtime environment 
for pygame games, inspired by most famous leading consoles such as 
PlayStation, Steam Deck, Nintendo Switch, and more.

Pygame is a small but passionate community that has been growing 
for years. However, most pygame projects are distributed as standalone 
apps without a unified launcher, system UI, or console-style experience. 
This project aims to change that.

Pygame Console APP transforms pygame into a console-like platform, 
where games run inside a managed environment with a consistent UI, 
navigation system, and controller-friendly experience — similar to 
how modern gaming consoles operate.

## 🎮 Vision

The goal of this project is to create a lightweight console OS built 
entirely with Python and Pygame that:

- Boots into a custom UI (like a real console)
- Supports controller and keyboard navigation
- Launches and manages pygame games
- Provides settings, themes, and system animations
- Runs on low-power hardware like Raspberry Pi Zero 2 W
- Can be turned into a handheld console device (Steam Deck–style)

This is not just a launcher — it is a runtime ecosystem for pygame games.

## 🧠 Core Concept

Instead of running pygame games directly, each game runs inside 
the Pygame Console APP environment.

The system provides:
- Boot animation
- Game library grid/list view
- Game metadata system (icon, description, version, author)
- Input abstraction layer (keyboard, controller, GPIO buttons)
- Settings manager (JSON-based)
- Smooth transitions and UI effects
- Game packaging support (e.g., zip loading)

Architecture Flow:
```bash
Your Game → Pygame Console Runtime → Hardware
```

# 🎯 Why This Project Matters

Pygame has always been powerful but fragmented. Pygame Console APP aims to create:
- A unified platform
- A more professional feel for pygame games
- A console-style experience
- A bridge between hobby development and console design
- A real hardware gaming device powered by Python

This project is both a software engineering challenge and a hardware 
engineering experiment.

# 🛠 Development Status

Currently in active development.

### Implemented
- Boot animation
- Home UI
- Navigation system
- Basic game launching
- Settings saving/loading

### In Progress
- Improved focus logic
- Better controller handling
- Performance optimization for Pi Zero 2 W or Pi 5

