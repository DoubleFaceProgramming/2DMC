import os
import sys
import pygame
from random import *
from pygame.locals import *
from pygame.math import Vector2 as VEC

FPS = 144
WIDTH, HEIGHT = 768, 768
BG_COLOR = (135, 206, 250)
BLOCK_SIZE = 16
CHUNK_SIZE = 8
CHUNK_PIXEL_SIZE = BLOCK_SIZE * CHUNK_SIZE

inttup = lambda tup: tuple((int(tup[0]), int(tup[1])))
intvec = lambda vec: VEC((int(vec[0]), int(vec[1])))

def canter_pairing(tup: tuple) -> int:
    """Uses the Canter Pairing function to get a unique integer from a unique interger pair"""
    # Deal with negative numbers by turning positives into positive evens and negatives into positive odds
    a = 2 * tup[0] if tup[0] >= 0 else -2 * tup[0] - 1
    b = 2 * tup[1] if tup[1] >= 0 else -2 * tup[1] - 1
    return (a + b) * (a + b + 1) + b

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | HWSURFACE)
clock = pygame.time.Clock()

block_images = {filename[:-4]: pygame.image.load(f"assets/{filename}").convert_alpha() for filename in os.listdir("assets")} | {"air": pygame.Surface((0, 0))}

class PosDict(dict):
    """Custom dictionary that can take Vectors and turn them into tuples for hashing, doesn't error if key doesn't exist"""
    def __getitem__(self, key):
        return super().__getitem__(inttup(key))

    def __setitem__(self, key, value):
        super().__setitem__(inttup(key), value)

    def __delitem__(self, key):
        return super().__delitem__(inttup(key))

    def __contains__(self, key):
        return super().__contains__(inttup(key))

    def __missing__(self, key):
        return ""

class BlockDict(PosDict):
    """Custom dictionary that returns air for non-existent positions"""
    def __setitem__(self, key, value):
        if value == "air": return
        return super().__setitem__(key, value)

    def __missing__(self, key):
        return "air"

class ChunkData(BlockDict):
    """Custom dictionary that also has methods that handle chunk generation"""
    def __init__(self, chunk_pos):
        self.chunk_pos = chunk_pos
        self.fill("stone")

    def fill(self, block_name):
        seed(canter_pairing(self.chunk_pos))
        for y in range(CHUNK_SIZE):
            for x in range(CHUNK_SIZE):
                self[(x, y)] = block_name

class Chunk:
    """Renders a chunk"""
    instances = PosDict()

    def __init__(self, chunk_pos: tuple):
        self.__class__.instances[chunk_pos] = self
        self.chunk_pos = intvec(chunk_pos)
        self.chunk_data = ChunkData(self.chunk_pos)
        self.image = pygame.Surface((CHUNK_PIXEL_SIZE, CHUNK_PIXEL_SIZE), SRCALPHA)
        for block_pos, block_name in self.chunk_data.items():
            self.image.blit(block_images[block_name], VEC(block_pos) * BLOCK_SIZE)

    def draw(self):
        screen.blit(self.image, self.chunk_pos * CHUNK_PIXEL_SIZE)

running = True
while running:
    clock.tick_busy_loop(FPS)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                mpos = VEC(pygame.mouse.get_pos())
                chunk_pos = mpos / CHUNK_PIXEL_SIZE
                if chunk_pos in Chunk.instances:
                    del Chunk.instances[chunk_pos]
                else:
                    Chunk(chunk_pos)

    screen.fill(BG_COLOR)

    for chunk in Chunk.instances.values():
        chunk.draw()

    pygame.display.flip()

pygame.quit()
sys.exit()