from pygame.draw import rect as drawrect
from pygame.surface import Surface
from pygame import Rect
from pygame.locals import SRCALPHA
import os
from src.constants import *

def pathof(file):
    abspath = os.path.abspath(os.path.join(BUNDLE_DIR, file))
    if not os.path.exists(abspath):
        abspath = file
    return abspath

def intv(vector):
    return VEC(int(vector.x), int(vector.y))

def inttup(tup):
    return (int(tup[0]), int(tup[1]))

def text(text, color=(0, 0, 0)):
    return FONT24.render(text, True, color)

def smol_text(text, color=(255, 255, 255)):
    return FONT20.render(text, True, color)

def create_text_box(text, pos, opacity):
    text_rect = text.get_rect()
    blit_pos = pos
    surface = Surface((text_rect.width+16, text_rect.height+8), SRCALPHA)
    surface.set_alpha(opacity)
    drawrect(surface, (0, 0, 0), (2, 0, text_rect.width+12, text_rect.height+8))
    drawrect(surface, (0, 0, 0), (0, 2, text_rect.width+16, text_rect.height+4))
    drawrect(surface, (44, 8, 99), (2, 2, text_rect.width+12, 2))
    drawrect(surface, (44, 8, 99), (2, 4+text_rect.height, text_rect.width+12, 2))
    drawrect(surface, (44, 8, 99), (2, 2, 2, text_rect.height+4))
    drawrect(surface, (44, 8, 99), (12+text_rect.width, 2, 2, text_rect.height+4))
    surface.blit(text, (8, 4))
    return surface, blit_pos

def block_collide(playerx, playery, width, height, block, detecting):
    a_rect = Rect(playerx, playery, width, height)
    block_rect = Rect(block.pos.x, block.pos.y, BLOCK_SIZE, BLOCK_SIZE)
    detecting.append(block.rect)
    if a_rect.colliderect(block_rect):
        return True, detecting
    return False, detecting