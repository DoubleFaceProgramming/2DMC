from pygame.math import Vector2 as VEC
from enum import Enum, auto
from pygame.locals import *
import fastenum
import pygame

if not fastenum.enabled: fastenum.enable()

FPS = float("inf")
WIDTH, HEIGHT = 448, 448
BLOCK_SIZE = 64
NEIGHBORS = [VEC(0, -1), VEC(-1, 0), VEC(1, 0), VEC(0, 1)]

inttup = lambda tup: (int(tup[0]), int(tup[1]))

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | HWSURFACE)

def filled_surf(size, color, flags=SRCALPHA):
    surf = pygame.Surface(size, flags)
    surf.fill(color)
    return surf

class Blocks(Enum):
    grass_block = pygame.transform.scale(pygame.image.load("grass_block.png"), (BLOCK_SIZE, BLOCK_SIZE)).convert()
    dirt = pygame.transform.scale(pygame.image.load("dirt.png"), (BLOCK_SIZE, BLOCK_SIZE)).convert()

class WorldSlice(Enum):
    background = auto()
    middleground = auto()
    foreground = auto()

class SliceDarken(Enum):
    background = 0.72
    middleground = 0.86
    foreground = 1