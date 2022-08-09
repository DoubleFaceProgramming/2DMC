import os
import sys
import pygame
from random import *
from pygame.locals import *
from enum import Enum, auto
from typing import Generator
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

class WorldSlices(Enum):
    BACKGROUND = auto()
    MIDDLEGROUND = auto()
    FOREGROUND = auto()

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

def generate_location(coords: tuple[int, int]) -> tuple[str | None, str | None, str | None]:
    """Generate the names of the blocks to go at a certain location. Temporary world gen!"""

    coords = VEC(coords)
    if coords.y == 4:
        name = "grass_block"
    elif 4 < coords.y <= 8:
        name = "dirt"
    elif coords.y > 8:
        name = choice(["stone", "andesite"])
    else:
        name = None
    return (name, name, name) # Veru temporary - we want all slices to be the same

class Block:
    def __init__(self, master, name: str, worldslice: WorldSlices | int) -> None:
        self.master = master
        self.name = name
        self.data = {}
        self.image = block_images[self.name]
        self.worldslice = WorldSlices(worldslice)

class Location:
    instances = PosDict()

    def __init__(self, master, coords: tuple[int, int], bg: None | Block = None, mg: None | Block = None, fg: None | Block = None):
        self.master = master
        self.coords = VEC(coords)
        self.__class__.instances[self.coords] = self
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), SRCALPHA)

        self.blocks: list[Block | None, Block | None, Block | None] = [
            Block(self, bg, WorldSlices.BACKGROUND  ) if bg else None,
            Block(self, mg, WorldSlices.MIDDLEGROUND) if mg else None,
            Block(self, fg, WorldSlices.FOREGROUND  ) if fg else None
        ]
        self.update_image()

    def __getitem__(self, key: WorldSlices | int):
        return self.blocks[WorldSlices(key)]

    def __setitem__(self, key: WorldSlices | int, value):
        self.blocks[WorldSlices(key)] = value
        self.update_image()
        self.master.update_image(self.coords, self.image)

    def __delitem__(self, key: WorldSlices | int):
        self.blocks[WorldSlices(key)] = None
        self.update_image()
        self.master.update_image(self.coords, self.image)

    def __contains__(self, key: WorldSlices | int):
        return bool(WorldSlices(key))

    def update_image(self):
        for block in self.highest_opaque_block():
            if block:
                self.image.blit(block.image, (0, 0))

    # TODO: use tag system for transparency
    def highest_opaque_block(self):
        """Get the blocks from the highest opaque block to the foreground"""
        rev = self.blocks.copy()
        rev.reverse()
        for index, block in enumerate(rev):
            if not block: continue
            if block.name not in {"glass", "tall_grass", "tall_grass_top", "grass", "dandelion", "poppy"}: # <- tags go here
                new = rev[:index + 1] # Return all blocks from the highest opaque block (index + 1) to the foreground
                new.reverse()
                return new

        return self.blocks # If the are no opaque blocks return self.blocks

class ChunkData(PosDict):
    """Custom dictionary that also has methods that handle chunk generation"""
    def __init__(self, master, chunk_pos: tuple[int, int] | VEC) -> None:
        self.master = master
        self.chunk_pos = VEC(chunk_pos)
        self.generate_base()

    def iterate(self) -> Generator:
        """Iterates through every coordinate inside the chunk, yields the absolute coordinates, NOT chunk coordinates"""
        for y in range(int(self.chunk_pos.y * CHUNK_SIZE), int(self.chunk_pos.y * CHUNK_SIZE + CHUNK_SIZE)):
            for x in range(int(self.chunk_pos.x * CHUNK_SIZE), int(self.chunk_pos.x * CHUNK_SIZE + CHUNK_SIZE)):
                yield (x, y)

    def generate_base(self) -> None:
        """Generate every block in the chunk"""
        seed(pairing(3, *self.chunk_pos, SEED))
        for pos in self.iterate():
            self[pos] = Location(self.master, pos, *generate_location(pos))

class Chunk:
    instances = PosDict()
    
    def __init__(self, chunk_pos: tuple[int, int] | VEC, chunk_data=None) -> None:
        self.__class__.instances[chunk_pos] = self
        self.chunk_pos = VEC(chunk_pos)
        if not chunk_data:
            self.chunk_data = ChunkData(self, self.chunk_pos)
        else:
            self.chunk_data = chunk_data
        self.image = pygame.Surface((CHUNK_PIXEL_SIZE, CHUNK_PIXEL_SIZE), SRCALPHA)
        # Updates every location on the chunk as the chunk was just created
        for coords, location in self.chunk_data.items():
            self.update_image(VEC(coords), location.image)

    def update_image(self, coords: tuple[int, int], image: pygame.Surface) -> None:
        """Update the image of a location on it's parent chunk."""
        on_chunk_pos = VEC(coords.x % CHUNK_SIZE, coords.y % CHUNK_SIZE) * BLOCK_SIZE
        self.image.fill((0, 0, 0, 0), (*on_chunk_pos, BLOCK_SIZE, BLOCK_SIZE)) # Clear the area that the image occupies
        self.image.blit(image, on_chunk_pos)

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
                chunk_pos = mpos // CHUNK_PIXEL_SIZE
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