from ui.carousel import Carousel
from ui.info_panel import InfoPanel

class GamesScreen:
    def __init__(self, font_title, font_meta, font_label):
        self.carousel = Carousel(font_title=font_title, font_meta=font_meta)
        self.info_panel = InfoPanel(
            font_title=font_title, font_label=font_label, font_body=font_meta
        )

    def handle_input(self, actions, filtered):
        if actions["LEFT"]:
            self.carousel.move_left(len(filtered))
            self.info_panel.close()
        if actions["RIGHT"]:
            self.carousel.move_right(len(filtered))
            self.info_panel.close()
        if actions["DETAIL"]:
            game = self.carousel.get_selected_game(filtered)
            if game:
                self.info_panel.toggle(game)
        if actions["BACK"] and self.info_panel.is_open:
            self.info_panel.close()

        # Returns selected game if ACCEPT pressed, else None
        if actions["ACCEPT"]:
            return self.carousel.get_selected_game(filtered)
        return None

    def update(self, dt, filtered):
        self.carousel.update(dt)
        if self.carousel.selected >= len(filtered):
            self.carousel.set_selected(max(0, len(filtered) - 1), len(filtered))

    def draw(self, screen, theme, filtered, content_rect, footer_height):
        self.carousel.draw(screen, theme, filtered, content_rect)
        self.info_panel.draw(screen, theme, footer_height=footer_height)
