import sys
import pygame
from random import *
from numpy import ndarray
from pygame.locals import *
from typing import Generator
from pygame.math import Vector2 as VEC
from pyfastnoisesimd import Noise, NoiseType, FractalType, PerturbType

import time
from my_profile import profile_chunk

from block import Location
from constants import *
from utils import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | HWSURFACE)
clock = pygame.time.Clock()

# 0.00012 secs on avg
noise = Noise(SEED)
noise.noiseType = NoiseType.PerlinFractal
noise.frequency = 0.01
noise.fractal.fractalType = FractalType.Billow
noise.fractal.octaves = 3
noise.fractal.lacunarity = 0.5
noise.fractal.gain = 1
noise.perturb.perturbType = PerturbType.Gradient
noise.perturb.amp = 2
noise.perturb.frequency = 0.2

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

    # Only generate the background is theres a cave
    return (name,) if cave else (name, name)

class ChunkData(PosDict):
    """Custom dictionary that also has methods that handle chunk generation"""
    def __init__(self, master, chunk_pos: tuple[int, int] | VEC) -> None:
        self.master = master
        self.chunk_pos = VEC(chunk_pos)
        self.generate_base()

    def iterate(self) -> Generator:
        """Iterates through every coordinate inside the chunk, yields the absolute coordinates AND chunk coordinates"""
        for y in range(CHUNK_SIZE):
            for x in range(CHUNK_SIZE):
                yield (x + self.chunk_pos.x * CHUNK_SIZE, y + self.chunk_pos.y * CHUNK_SIZE), (x, y)

    def generate_cave_map(self) -> ndarray:
        """Creates a numpy ndarray storing the heightmap for cave generation"""
        return noise.genAsGrid([CHUNK_SIZE, CHUNK_SIZE, 1], [int(self.chunk_pos.x * CHUNK_SIZE), int(self.chunk_pos.y * CHUNK_SIZE), 0]).tolist()
    
    def is_cave(self, pos: tuple | VEC) -> bool:
        """Determines if a position is in a cave based on the noise map"""
        return -0.55 < self.noise_map[pos[0]][pos[1]][0] < -0.48

    def generate_base(self) -> None:
        """Generate every block in the chunk"""
        seed(pairing(3, *self.chunk_pos, SEED))
        self.noise_map = self.generate_cave_map()
        for pos, in_chunk_pos in self.iterate():
            self[pos] = Location(self.master, pos, *generate_location(pos, self.is_cave(in_chunk_pos)))

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
            self.update_image(VEC(coords), location.image, first=True)

    def update_image(self, coords: tuple[int, int], image: pygame.Surface, first: bool = False) -> None:
        """Update the image of a location on it's parent chunk."""
        on_chunk_pos = (coords.x % CHUNK_SIZE * BLOCK_SIZE, coords.y % CHUNK_SIZE * BLOCK_SIZE)
        if not first:
            self.image.fill((0, 0, 0, 0), (*on_chunk_pos, BLOCK_SIZE, BLOCK_SIZE)) # Clear the area that the image occupies
        self.image.blit(image, on_chunk_pos)

    def draw(self) -> None:
        screen.blit(self.image, self.chunk_pos * CHUNK_PIXEL_SIZE)
        # pygame.draw.rect(screen, (255, 255, 0), (self.chunk_pos * CHUNK_PIXEL_SIZE, self.image.get_size()), 1)

start = time.time()
avg = 0
for x in range(WIDTH // CHUNK_PIXEL_SIZE):
    for y in range(HEIGHT // CHUNK_PIXEL_SIZE):
        one_chunk_start = time.time()
        Chunk((x, y))
        avg += time.time() - one_chunk_start
        avg /= 2
print("TOTAL:", time.time() - start, "seconds")
print("AVERAGE:", avg, "seconds")

# Uncomment for cool gradual generation :)
# x = y = 0

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
                        profile_chunk(Chunk, chunk_pos)
                    else:
                        Chunk(chunk_pos)
            if event.button == 3:
                block_pos = mpos // BLOCK_SIZE
                if block_pos in Location.instances:
                    location = Location.instances[block_pos]
                    del location[location.get_highest()]
    
    # Uncomment for cool gradual generation :)
    # if x < WIDTH // CHUNK_PIXEL_SIZE + 1:
    #     Chunk((x, y))
    #     x += 1
    # elif y < HEIGHT // CHUNK_PIXEL_SIZE - 1:
    #     x = 0
    #     y += 1
    # print(len(Chunk.instances))

    screen.fill(BG_COLOR)

    for chunk in Chunk.instances.values():
        chunk.draw()

    pygame.display.flip()

pygame.quit()
sys.exit()