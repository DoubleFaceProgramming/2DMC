import os
import sys
import pygame
from random import *
from pygame.locals import *
from pygame.math import Vector2 as VEC

FPS = 144
WIDTH, HEIGHT = 1280, 768
BG_COLOR = (135, 206, 250)
BLOCK_SIZE = 16 # Number of pixels in a block
CHUNK_SIZE = 8 # Number of blocks in a chunk
CHUNK_PIXEL_SIZE = BLOCK_SIZE * CHUNK_SIZE # Size in pixels of a chunk
SEED = 1

inttup = lambda tup: tuple((int(tup[0]), int(tup[1])))
intvec = lambda vec: VEC((int(vec[0]), int(vec[1])))

def pairing(count, *args: int) -> int:
    count -= 1
    if count == 0: return int(args[0])
    a = 2 * args[0] if args[0] >= 0 else -2 * args[0] - 1
    b = 2 * args[1] if args[1] >= 0 else -2 * args[1] - 1
    new = [0.5 * (a + b) * (a + b + 1) + b] + [num for i, num in enumerate(args) if i > 1]
    return pairing(count, *new)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | HWSURFACE)
clock = pygame.time.Clock()

# Loads each image in assets, also adds a key for air so that when air is hashed, it doesn't error
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
        # If an air block gets created, it would have to be deleted at some point, thus don't even create it
        if value.name == "air": return
        return super().__setitem__(key, value)

    def __missing__(self, key):
        return "air"

class BlockData:
    """Class for storing and generating a single block"""
    def __init__(self, pos, name=None):
        self.pos = VEC(pos)
        if name is not None:
            self.name = name
        else:
            self.generate()

    def generate(self):
        if self.pos.y == 4:
            self.name = "grass_block"
        elif 4 < self.pos.y <= 8:
            self.name = "dirt"
        elif self.pos.y > 8:
            self.name = choice(["stone", "andesite"])
        else:
            self.name = "air"

class ChunkData(BlockDict):
    """Custom dictionary that also has methods that handle chunk generation"""
    def __init__(self, chunk_pos):
        self.chunk_pos = chunk_pos
        self.generate_base()

    def iterate(self):
        for y in range(int(self.chunk_pos.y * CHUNK_SIZE + CHUNK_SIZE)):
            for x in range(int(self.chunk_pos.x * CHUNK_SIZE + CHUNK_SIZE)):
                yield (x, y)

    def generate_base(self):
        seed(pairing(3, *self.chunk_pos, SEED))
        for pos in self.iterate():
            self[pos] = BlockData(pos)

    def fill(self, block_name):
        seed(pairing(3, *self.chunk_pos, SEED))
        for pos in self.iterate():
            self[pos] = BlockData(pos, block_name)

class Chunk:
    """Renders a chunk"""
    instances = PosDict()

    def __init__(self, chunk_pos: tuple):
        self.__class__.instances[chunk_pos] = self
        self.chunk_pos = intvec(chunk_pos)
        self.chunk_data = ChunkData(self.chunk_pos)
        self.image = pygame.Surface((CHUNK_PIXEL_SIZE, CHUNK_PIXEL_SIZE), SRCALPHA)
        # Blit every block's image onto the chunk's image
        for block_pos, block in self.chunk_data.items():
            self.image.blit(block_images[block.name], VEC(block_pos - self.chunk_pos * CHUNK_SIZE) * BLOCK_SIZE)

    def draw(self):
        screen.blit(self.image, self.chunk_pos * CHUNK_PIXEL_SIZE)
        pygame.draw.rect(screen, (255, 255, 0), (self.chunk_pos * CHUNK_PIXEL_SIZE, self.image.get_size()), 1)

running = True
while running:
    clock.tick_busy_loop(FPS)
    pygame.display.set_caption("Chunk Loading Tester")

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