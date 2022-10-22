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
NEIGHBORS = [VEC(0, -1), VEC(-1, 0), VEC(1, 0), VEC(0, 1)]

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

class SliceDarken(Enum):
    background = 0.78
    middleground = 0.88
    foreground = 1

class Block:
    instances = {}

    def __init__(self, pos: tuple[int, int], block: Blocks, worldslice: WorldSlice) -> None:
        self.__class__.instances[pos] = self
        self.coords = VEC(pos)
        self.pos = self.coords * BLOCK_SIZE
        self.block = block
        self.worldslice = worldslice

    def update(self) -> None:
        instances = self.__class__.instances
        neighbors = []
        for offset in NEIGHBORS:
            block_pos = inttup(self.coords + offset)
            if block_pos in instances and instances[block_pos].worldslice.value > self.worldslice.value:
                neighbors.append(inttup(offset))
        self.neighbors = tuple(neighbors)

    def draw(self) -> None:
        if self.coords == (3, 2): # Temporary for testing purposes
            self.image = apply_vignette(self.block.value, kernel_2x3_top, darken=0.8) # Very annoying scenerio, can't be easily solved with a simple gaussian kernel
        else:
            self.image = apply_vignette(self.block.value, vignette_lookup[self.neighbors], darken=SliceDarken[self.worldslice.name].value)
        screen.blit(self.image, self.pos)

    def kill(self) -> None:
        self.__class__.instances[inttup(self.coords)]

legend = {
    "1": (Blocks.dirt, WorldSlice.foreground),
    "2": (Blocks.dirt, WorldSlice.middleground),
    "3": (Blocks.dirt, WorldSlice.background),
    "4": (Blocks.grass_block, WorldSlice.foreground),
    "5": (Blocks.grass_block, WorldSlice.middleground),
}
blocks = [
    "4444444",
    "1212121",
    "1122211",
    "0233320",
    "0233320",
    "0122210",
    "0000000"
]

for y, row in enumerate(blocks):
    for x, ch in enumerate(row):
        if ch not in legend: continue
        Block((x, y), *legend[ch])

running = True
while running:
    clock.tick_busy_loop(FPS)
    pygame.display.set_caption(f"Vignette Test | {clock.get_fps():.2f}")

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