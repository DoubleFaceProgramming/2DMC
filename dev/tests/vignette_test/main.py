from pygame.math import Vector2 as VEC
from enum import Enum, auto
from pygame.locals import *
import fastenum
import pygame
import sys

from vignette import *

if not fastenum.enabled: fastenum.enable()

inttup = lambda tup: (int(tup[0]), int(tup[1]))

FPS = 144
WIDTH, HEIGHT = 448, 448
BLOCK_SIZE = 64

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | HWSURFACE)
clock = pygame.time.Clock()

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

class SliceOverlay(Enum):
    background = filled_surf((BLOCK_SIZE, BLOCK_SIZE), (0, 0, 0, 70))
    middleground = filled_surf((BLOCK_SIZE, BLOCK_SIZE), (0, 0, 0, 40))
    foreground = pygame.Surface((0, 0))

class Block:
    instances = {}

    def __init__(self, pos: tuple[int, int], block: Blocks, worldslice: WorldSlice) -> None:
        self.__class__.instances[pos] = self
        self.coords = VEC(pos)
        self.pos = self.coords * BLOCK_SIZE
        self.block = block
        self.worldslice = worldslice
        if self.coords == (2, 2):
            self.image = apply_vignette(self.block.value, kernel_3x3_1)
        elif self.coords == (4, 2):
            self.image = apply_vignette(self.block.value, kernel_3x3_3)
        elif self.coords == (2, 4):
            self.image = apply_vignette(self.block.value, kernel_3x3_7)
        elif self.coords == (4, 4):
            self.image = apply_vignette(self.block.value, kernel_3x3_9)
        elif self.coords.x == 2:
            self.image = apply_vignette(self.block.value, kernel_3x3_4)
        elif self.coords.x == 4:
            self.image = apply_vignette(self.block.value, kernel_3x3_6)
        elif self.coords.y == 2:
            self.image = apply_vignette(self.block.value, kernel_3x3_2)
        elif self.coords.y == 4:
            self.image = apply_vignette(self.block.value, kernel_3x3_8)
        else:
            self.image = apply_vignette(self.block.value, kernel_3x3_5)

    def update(self) -> None:
        pass

    def draw(self) -> None:
        screen.blit(self.image, self.pos)

    def kill(self) -> None:
        self.__class__.instances[inttup(self.coords)]

Block((1, 1), Blocks.grass_block, WorldSlice.middleground)
Block((2, 1), Blocks.grass_block, WorldSlice.middleground)
Block((3, 1), Blocks.grass_block, WorldSlice.middleground)
Block((4, 1), Blocks.grass_block, WorldSlice.middleground)
Block((5, 1), Blocks.grass_block, WorldSlice.middleground)
Block((5, 2), Blocks.dirt, WorldSlice.middleground)
Block((5, 3), Blocks.dirt, WorldSlice.middleground)
Block((5, 4), Blocks.dirt, WorldSlice.middleground)
Block((5, 5), Blocks.dirt, WorldSlice.middleground)
Block((4, 5), Blocks.dirt, WorldSlice.middleground)
Block((3, 5), Blocks.dirt, WorldSlice.middleground)
Block((2, 5), Blocks.dirt, WorldSlice.middleground)
Block((1, 5), Blocks.dirt, WorldSlice.middleground)
Block((1, 4), Blocks.dirt, WorldSlice.middleground)
Block((1, 3), Blocks.dirt, WorldSlice.middleground)
Block((1, 2), Blocks.dirt, WorldSlice.middleground)

Block((2, 2), Blocks.dirt, WorldSlice.background)
Block((3, 2), Blocks.dirt, WorldSlice.background)
Block((4, 2), Blocks.dirt, WorldSlice.background)
Block((2, 3), Blocks.dirt, WorldSlice.background)
Block((3, 3), Blocks.dirt, WorldSlice.background)
Block((4, 3), Blocks.dirt, WorldSlice.background)
Block((2, 4), Blocks.dirt, WorldSlice.background)
Block((3, 4), Blocks.dirt, WorldSlice.background)
Block((4, 4), Blocks.dirt, WorldSlice.background)

running = True
while running:
    clock.tick_busy_loop(FPS)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    for block in Block.instances.values():
        block.update()

    screen.fill((135, 206, 250))
    for block in Block.instances.values():
        block.draw()

    pygame.display.flip()

pygame.quit()
sys.exit()