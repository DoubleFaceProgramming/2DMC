import pygame
from pygame import Surface
from pygame.locals import SRCALPHA
import time

from src.constants import VEC
from src.utils import smol_text, inttup

class TextBox:
    def __init__(self, text: str, pos: tuple, survive_time: float = None, centered: tuple[bool, bool] = (False, False)):
        self.text = text
        self.text_surf = smol_text(self.text)
        self.pos = VEC(pos)
        self.survive_time = survive_time
        self.centered = centered
        self.opacity = 255
        
    def update(self):
        if self.survive_time:
            if (time_elapsed := time.time() - self.fade_timer) < self.survive_time:
                self.opacity = 255 * (self.survive_time - time_elapsed) if time_elapsed > self.survive_time * 2/3 else 255
            else:
                del self

    def draw(self, screen):
        # Creating a surface slightly larger than the text and changing opacity
        text_rect = self.text_surf.get_rect()
        surface = Surface((text_rect.width+16, text_rect.height+8), SRCALPHA)
        surface.set_alpha(self.opacity)

        # Drawing a bunch of rects the make the minecraft style purple border
        pygame.draw.rect(surface, (0, 0, 0), (2, 0, text_rect.width + 12, text_rect.height + 8))
        pygame.draw.rect(surface, (0, 0, 0), (0, 2, text_rect.width + 16, text_rect.height + 4))
        pygame.draw.rect(surface, (44, 8, 99), (2, 2, text_rect.width + 12, 2))
        pygame.draw.rect(surface, (44, 8, 99), (2, 4 + text_rect.height, text_rect.width + 12, 2))
        pygame.draw.rect(surface, (44, 8, 99), (2, 2, 2, text_rect.height + 4))
        pygame.draw.rect(surface, (44, 8, 99), (12 + text_rect.width, 2, 2, text_rect.height + 4))

        # Blitting the text onto the surface
        surface.blit(self.text_surf, (8, 4))
        
        # If centered[0] is True, it means the text box will be blitted centered on the x-pos
        if self.centered[0]:
            self.pos.x -= text_rect.width / 2
        if self.centered[1]:
            self.pos.y -= text_rect.height / 2
        screen.blit(surface, inttup(self.pos))