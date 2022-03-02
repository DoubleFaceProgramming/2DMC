from pygame.draw import rect as drawrect
from pygame.locals import SRCALPHA
from pygame import Rect, Surface
import time

from src.utils import smol_text, ultra_smol_text
from src.sprite import LayersEnum, Sprite
from src.constants import VEC, Anchors

class TextBox(Sprite):
    def __init__(self, layer: LayersEnum, text: str, pos: tuple[int, int], survive_time: float = None, anchor: Anchors = Anchors.TOPLEFT):
        super().__init__(layer)

        # Text attributes
        self.text = text
        self.text_surf = smol_text(self.text)
        text_rect = self.text_surf.get_rect()

        # Size and positions attributes (size is slightly bigger than the text)
        self.anchor = VEC(anchor.value)
        self.size = VEC(text_rect.width + 16, text_rect.height + 8)
        self.pos = VEC(pos) - VEC(self.anchor.x * self.size.x, self.anchor.y * self.size.y) // 2

        # Time attributes
        self.survive_time = survive_time
        self.start_time = time.time()

        # Creating an image with full opacity
        self.opacity = 255
        self.image = Surface(self.size, SRCALPHA)
        self.image.set_alpha(self.opacity)

        # Drawing a magenta border to give it a minecraft feel and blit the text on
        drawrect(self.image, (0, 0, 0), (2, 0, text_rect.width + 12, text_rect.height + 8))
        drawrect(self.image, (0, 0, 0), (0, 2, text_rect.width + 16, text_rect.height + 4))
        drawrect(self.image, (44, 8, 99), (2, 2, text_rect.width + 12, 2))
        drawrect(self.image, (44, 8, 99), (2, 4 + text_rect.height, text_rect.width + 12, 2))
        drawrect(self.image, (44, 8, 99), (2, 2, 2, text_rect.height + 4))
        drawrect(self.image, (44, 8, 99), (12 + text_rect.width, 2, 2, text_rect.height + 4))
        self.image.blit(self.text_surf, (8, 4))
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos

    def update(self, dt: float, **kwargs):
        self.rect.topleft = self.pos
        if self.survive_time: # If the text box shouldnt last for an infite time
            if (time_elapsed := time.time() - self.start_time) < self.survive_time:
                # Change the opacity based on the text box's lifetime
                self.opacity = 255 * (self.survive_time - time_elapsed) if time_elapsed > self.survive_time * 2/3 else 255
                self.image.set_alpha(self.opacity)
            else: # If the text box has lived longer than the survive time, kill it
                super().kill()

    def draw(self, screen: Surface, **kwargs):
        screen.blit(self.image, self.rect)

    def debug(self, screen, **kwargs) -> None:
        if self.survive_time:
            debug_text = ultra_smol_text(f"Time elapsed: {time.time() - self.start_time:.2f}") # Rounding the time to 2 decimal places
            debug_text.set_alpha(self.opacity)
            rect = Rect(self.rect.left, self.rect.top - self.rect.height / 2, debug_text.get_width(), debug_text.get_height())
            rect.centerx = self.rect.centerx # Centering the text
            screen.blit(debug_text, rect)
        drawrect(screen, (255, 0, 0), self.rect, width=1) # Drawing an outline rect