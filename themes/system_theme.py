import pygame

THEMES_DATA = [
    {
        "name": "MIDNIGHT",
        "type": "solid",
        "colors": {
            "bg": (18, 18, 24),
            "header": (32, 32, 40),
            "accent": (0, 255, 150),
            "text": (245, 245, 245),
            "btn": (60, 60, 75),
            "panel": (28, 28, 36),
            "border": (60, 60, 75),
        },
    },
    {
        "name": "SWITCH NEON",
        "type": "solid",
        "colors": {
            "bg": (235, 235, 235),
            "header": (255, 255, 255),
            "accent": (255, 60, 60),
            "text": (45, 45, 45),
            "btn": (0, 190, 255),
            "panel": (255, 255, 255),
            "border": (200, 200, 200),
        },
    },
    {
        "name": "3DS WHITE",
        "type": "solid",
        "colors": {
            "bg": (245, 245, 245),
            "header": (255, 255, 255),
            "accent": (160, 160, 160),
            "text": (70, 70, 70),
            "btn": (120, 120, 120),
            "panel": (255, 255, 255),
            "border": (210, 210, 210),
        },
    },
    {
        "name": "GAMEBOY",
        "type": "solid",
        "colors": {
            "bg": (155, 188, 15),
            "header": (139, 172, 15),
            "accent": (48, 98, 48),
            "text": (15, 56, 15),
            "btn": (48, 98, 48),
            "panel": (139, 172, 15),
            "border": (15, 56, 15),
        },
    },
    {
        "name": "KAWAII",
        "type": "solid",
        "colors": {
            "bg": (255, 245, 250),
            "header": (255, 255, 255),
            "accent": (255, 120, 190),
            "text": (110, 60, 60),
            "btn": (255, 190, 210),
            "panel": (255, 255, 255),
            "border": (255, 200, 220),
        },
    },
    # Example future art theme:
    # {
    #     "name": "RETRO ARCADE",
    #     "type": "image",
    #     "background_path": ("assets", "themes", "retro_arcade", "bg.png"),
    #     "colors": {
    #         "bg": (10, 10, 20),       # fallback if image fails
    #         "header": (30, 30, 50),
    #         "accent": (255, 80, 0),
    #         "text": (255, 255, 255),
    #         "btn": (50, 50, 80),
    #         "panel": (20, 20, 35),
    #         "border": (255, 80, 0),
    #     },
    # },
    # Example future video theme:
    # {
    #     "name": "CYBER WAVE",
    #     "type": "video",
    #     "background_path": ("assets", "themes", "cyber_wave", "bg_frames"),
    #     "frame_duration": 0.05,
    #     "colors": { ... },
    # },
]
