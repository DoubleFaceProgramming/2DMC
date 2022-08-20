import sys
import pygame
from random import *
from pygame.locals import *
from typing import Generator
from pyfastnoisesimd import Noise
from pygame.math import Vector2 as VEC

from my_profile import profile

from block import Location
from constants import *
from utils import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | HWSURFACE)
clock = pygame.time.Clock()

noise = Noise(SEED, 8)
noise.fractal.lacunarity = 0.8

def generate_location(coords: tuple[int, int], cave: bool) -> tuple[str | None, str | None, str | None]:
    """Generate the names of the blocks to go at a certain location. Temporary world gen!"""

    coords = VEC(coords)
    if coords.y == 4:
        name = "grass_block"
    elif 4 < coords.y <= 8:
        name = "dirt"
    elif coords.y > 8:
        name = "stone"
    else:
        name = None
    return (name,) if cave else (name, name)

class ChunkData(PosDict):
    """Custom dictionary that also has methods that handle chunk generation"""
    def __init__(self, master, chunk_pos: tuple[int, int] | VEC) -> None:
        self.master = master
        self.chunk_pos = VEC(chunk_pos)
        self.generate_base()

    def iterate(self) -> Generator:
        """Iterates through every coordinate inside the chunk, yields the absolute coordinates AND chunk coordinates"""
        for y in range(int(self.chunk_pos.y * CHUNK_SIZE), int(self.chunk_pos.y * CHUNK_SIZE + CHUNK_SIZE)):
            for x in range(int(self.chunk_pos.x * CHUNK_SIZE), int(self.chunk_pos.x * CHUNK_SIZE + CHUNK_SIZE)):
                yield (x, y), inttup((x - self.chunk_pos.x * CHUNK_SIZE, y - self.chunk_pos.y * CHUNK_SIZE))

    def generate_base(self) -> None:
        """Generate every block in the chunk"""
        seed(pairing(3, *self.chunk_pos, SEED))
        noise_grid = noise.genAsGrid([8, 8, 1], [int(self.chunk_pos.x * CHUNK_SIZE), int(self.chunk_pos.y * CHUNK_SIZE), 0])
        for pos, in_chunk_pos in self.iterate():
            self[pos] = Location(self.master, pos, *generate_location(pos, 0.145 < noise_grid[in_chunk_pos[0]][in_chunk_pos[1]][0] < 0.275))

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
        # pygame.draw.rect(screen, (255, 255, 0), (self.chunk_pos * CHUNK_PIXEL_SIZE, self.image.get_size()), 1)

for x in range(WIDTH // CHUNK_PIXEL_SIZE + 1):
    for y in range(HEIGHT // CHUNK_PIXEL_SIZE + 1):
        Chunk((x, y))

running = True
while running:
    clock.tick_busy_loop(FPS)
    pygame.display.set_caption(f"Chunk Loading Tester {clock.get_fps():.0f}")

    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == MOUSEBUTTONDOWN:
            mpos = VEC(pygame.mouse.get_pos())
            if event.button == 1:
                chunk_pos = mpos // CHUNK_PIXEL_SIZE
                if chunk_pos in Chunk.instances:
                    del Chunk.instances[chunk_pos]
                else:
                    if keys[K_LSHIFT]:
                        profile(Chunk, chunk_pos)
                    else:
                        Chunk(chunk_pos)
            if event.button == 3:
                block_pos = mpos // BLOCK_SIZE
                if block_pos in Location.instances:
                    location = Location.instances[block_pos]
                    del location[location.get_highest()]

    screen.fill(BG_COLOR)

    for chunk in Chunk.instances.values():
        chunk.draw()

    pygame.display.flip()

pygame.quit()
sys.exit()