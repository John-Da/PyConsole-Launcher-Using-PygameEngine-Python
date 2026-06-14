import os
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
def booting_animation(
    screen,
    clock,
    APP_NAME,
    booting_music,
    fontstyle,
    themeslist,
    current_theme_idx,
    delay,
    boot_logo=None,
):
    theme = themeslist[current_theme_idx]
    ww, hh = screen.get_size()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pygame.mixer.music.load(booting_music)
    pygame.mixer.music.set_volume(0.7)
    pygame.mixer.music.play(fade_ms=300)

    fade_screen(screen, ww, hh, direction="in", speed=1, delay=delay)
    draw_loading_screen(screen, clock, fontstyle, theme, APP_NAME, logo=boot_logo)


def draw_loading_screen(screen, clock, fontstyle, theme, text="LOADING", logo=None):
    start_time = pygame.time.get_ticks()
    loading = True

    while loading:
        current_ticks = pygame.time.get_ticks()
        elapsed = current_ticks - start_time
        dt = clock.get_time() / 1000.0

        if elapsed < 1000:
            progress = (elapsed / 1000) * 0.15
        elif elapsed < 4000:
            progress = 0.15
        elif elapsed < 5000:
            progress = 0.15 + ((elapsed - 4000) / 1000) * (0.78 - 0.15)
        elif elapsed < 6000:
            progress = 0.78
        elif elapsed < 7000:
            progress = 0.78 + ((elapsed - 6000) / 1000) * (0.97 - 0.78)
        elif elapsed < 8500:
            progress = 0.97
        elif elapsed < 9500:
            progress = 0.97 + ((elapsed - 8500) / 1000) * (1.0 - 0.97)
        else:
            progress = 1.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        (
            theme.draw_background(screen)
            if hasattr(theme, "draw_background")
            else screen.fill(theme["bg"])
        )

        ww, hh = screen.get_width(), screen.get_height()
        cx, cy = ww // 2, hh // 2

        # Logo + App name (side by side, centered as a group)
        logo_surf = logo.current() if logo else None
        if logo:
            logo.update(dt)

        txt_surf = fontstyle.render(text.upper(), True, theme["text"])

        gap = 16
        logo_w = logo_surf.get_width() if logo_surf else 0
        group_w = logo_w + (gap if logo_surf else 0) + txt_surf.get_width()

        group_x = cx - group_w // 2
        group_y = cy - 50

        if logo_surf:
            logo_rect = logo_surf.get_rect(midleft=(group_x, group_y))
            screen.blit(logo_surf, logo_rect)
            text_x = logo_rect.right + gap
        else:
            text_x = group_x

        txt_rect = txt_surf.get_rect(midleft=(text_x, group_y))
        screen.blit(txt_surf, txt_rect)

        bar_y_anchor = (
            group_y
            + max(
                logo_surf.get_height() if logo_surf else 0,
                txt_surf.get_height(),
            )
            // 2
        )

        # Progress bar
        bar_w, bar_h = 400, 8
        bar_x, bar_y = cx - bar_w // 2, bar_y_anchor + 30

        draw_round_rect(
            screen, theme["header"], pygame.Rect(bar_x, bar_y, bar_w, bar_h), 4
        )
        draw_round_rect(
            screen,
            theme["accent"],
            pygame.Rect(bar_x, bar_y, int(bar_w * progress), bar_h),
            4,
        )

        pygame.display.flip()
        clock.tick(60)
        if progress >= 1.0:
            loading = False

def shutdown_animation(
    screen,
    clock,
    APP_NAME,
    closing_music,
    fontstyle,
    theme,
    delay=15,
    shutdown_logo=None,
    duration=5000,
):
    ww, hh = screen.get_size()

    txt_surf = fontstyle.render(
        f"SHUTTING DOWN {APP_NAME.upper()}...", True, theme["text"]
    )
    txt_rect = txt_surf.get_rect(center=(ww // 2, hh // 2 + 10))
    logo_center = (ww // 2, hh // 2 - 40)

    start_time = pygame.time.get_ticks()

    while pygame.time.get_ticks() - start_time < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        dt = clock.get_time() / 1000.0
        elapsed = pygame.time.get_ticks() - start_time
        alpha = int(155 + 100 * math.sin(elapsed * 0.006))

        screen.fill(theme["bg"])

        if shutdown_logo:
            shutdown_logo.update(dt)
            logo_surf = shutdown_logo.current()
            if logo_surf:
                screen.blit(logo_surf, logo_surf.get_rect(center=logo_center))

        txt_surf.set_alpha(alpha)
        screen.blit(txt_surf, txt_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.mixer.music.load(closing_music)
    pygame.mixer.music.set_volume(0.7)
    pygame.mixer.music.play(fade_ms=300)

    fade_screen(screen, ww, hh, direction="out", speed=2, delay=delay)
