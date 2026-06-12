import math
import sys

import pygame

from utils.helpers import terminate


# ======= Custom Rounded Buttons ================
def draw_round_rect(surf, color, rect, radius=10, border=0):
    if rect.width <= 0 or rect.height <= 0: return
    pygame.draw.rect(surf, color, rect, border, border_radius=radius)


# ======= Custom Console Buttons ================
def draw_console_btn(surf, text, rect, focused, fontstyle, theme, radius=10):
    bg = theme["accent"] if focused else theme["header"]
    txt_color = theme["bg"] if focused else theme["text"]
    draw_round_rect(surf, bg, rect, radius)
    if not focused: draw_round_rect(surf, theme["accent"], rect, radius, 2)
    t_surf = fontstyle.render(text.upper(), True, txt_color)
    surf.blit(t_surf, t_surf.get_rect(center=rect.center))


# ======= Fade IN/OUT Screen ================
def fade_screen(screen, width, height, direction='out', speed=5, delay=10):
    fade_surf = pygame.Surface((width, height))
    fade_surf.fill((0, 0, 0))
    if direction == 'out':
        for alpha in range(0, 256, speed):
            fade_surf.set_alpha(alpha)
            screen.blit(fade_surf, (0, 0))
            pygame.display.flip()
            pygame.time.delay(delay)
    else:
        for alpha in range(256, 0, -speed):
            fade_surf.set_alpha(alpha)
            screen.blit(fade_surf, (0, 0))
            pygame.display.flip()
            pygame.time.delay(delay)


# ======= Booting Animation Screen ================
def booting_animation(screen, clock, APP_NAME, booting_music, fontstyle, themeslist, current_theme_idx, delay):
    theme = themeslist[current_theme_idx]
    ww, hh = screen.get_size()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pygame.mixer.music.load(booting_music)
    pygame.mixer.music.set_volume(0.7)
    pygame.mixer.music.play(fade_ms=300)

    fade_screen(screen, ww, hh, direction='in', speed=1, delay=delay)
    draw_loading_screen(screen, clock, fontstyle, theme, f"...{APP_NAME}...")

    pygame.display.flip()
    pygame.time.delay(1200)


# ======== Loading Animation Screen ==================
def draw_loading_screen(screen, clock, fontstyle, theme, text="LOADING"):

    start_time = pygame.time.get_ticks()
    loading = True

    while loading:
        current_ticks = pygame.time.get_ticks()
        elapsed = current_ticks - start_time

        if elapsed < 1000:  # 0 → 15%
            progress = (elapsed / 1000) * 0.15

        elif elapsed < 4000:  # pause 3s
            progress = 0.15

        elif elapsed < 5000:  # 15 → 78%
            progress = 0.15 + ((elapsed - 4000) / 1000) * (0.78 - 0.15)

        elif elapsed < 6000:  # pause 1s
            progress = 0.78

        elif elapsed < 7000:  # 78 → 97%
            progress = 0.78 + ((elapsed - 6000) / 1000) * (0.97 - 0.78)

        elif elapsed < 8500:  # pause 1.5s
            progress = 0.97

        elif elapsed < 9500:  # 97 → 100%
            progress = 0.97 + ((elapsed - 8500) / 1000) * (1.0 - 0.97)

        else:
            progress = 1.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        screen.fill(theme["bg"])
        bar_w, bar_h = 400, 8
        bar_x, bar_y = (screen.get_width() - bar_w) // 2, (screen.get_height() // 2) + 40

        # Draw Bar
        draw_round_rect(screen, theme["header"], pygame.Rect(bar_x, bar_y, bar_w, bar_h), 4)
        draw_round_rect(screen, theme["accent"], pygame.Rect(bar_x, bar_y, int(bar_w * progress), bar_h), 4)

        # Pulsing Text
        alpha = int(155 + 100 * math.sin(current_ticks * 0.006))
        txt_surf = fontstyle.render(text, True, theme["text"])
        txt_surf.set_alpha(alpha)
        screen.blit(txt_surf, (screen.get_width() // 2 - txt_surf.get_width() // 2, bar_y - 40))

        pygame.display.flip()
        clock.tick(60)
        if progress >= 1.0: loading = False