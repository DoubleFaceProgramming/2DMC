from pygame.draw import rect as drawrect
from pygame.locals import SRCALPHA
from pygame import Surface
import time

from src.sprite import LayersEnum, Sprite
from src.utils import smol_text, inttup
from src.constants import VEC

class TextBox(Sprite):
    def __init__(self, layer: LayersEnum, text: str, pos: tuple[int, int], survive_time: float = None, centered: tuple[bool, bool] = (False, False)):
        super().__init__(layer)

        # Text attributes
        self.text = text
        self.text_surf = smol_text(self.text)
        text_rect = self.text_surf.get_rect()

        # Time attributes
        self.survive_time = survive_time
        self.start_time = time.time()

        # Size and positions attributes (size is slightly bigger than the text)
        self.size = (text_rect.width + 16, text_rect.height + 8)
        self.pos = VEC(pos)

        # Creating an image with full opacity
        self.image = Surface(self.size, SRCALPHA)
        self.image.set_alpha(255)

        # Drawing a magenta border to give it a minecraft feel and blit the text on
        drawrect(self.image, (0, 0, 0), (2, 0, text_rect.width + 12, text_rect.height + 8))
        drawrect(self.image, (0, 0, 0), (0, 2, text_rect.width + 16, text_rect.height + 4))
        drawrect(self.image, (44, 8, 99), (2, 2, text_rect.width + 12, 2))
        drawrect(self.image, (44, 8, 99), (2, 4 + text_rect.height, text_rect.width + 12, 2))
        drawrect(self.image, (44, 8, 99), (2, 2, 2, text_rect.height + 4))
        drawrect(self.image, (44, 8, 99), (12 + text_rect.width, 2, 2, text_rect.height + 4))
        self.image.blit(self.text_surf, (8, 4))

        # Center the text box
        if centered[0]:
            self.pos.x -= self.size.width / 2
        if centered[1]:
            self.pos.y -= self.size.height / 2

    def update(self, dt: float, **kwargs):
        if self.survive_time: # If the text box shouldnt last for an infite time
            if (time_elapsed := time.time() - self.start_time) < self.survive_time:
                # Change the opacity based on the text box's lifetime
                self.image.set_alpha(255 * (self.survive_time - time_elapsed) if time_elapsed > self.survive_time * 2/3 else 255)
            else: # If the text box has lived longer than the survive time, kill it
                super().kill()

    def draw(self, screen: Surface, **kwargs):
        screen.blit(self.image, inttup(self.pos))