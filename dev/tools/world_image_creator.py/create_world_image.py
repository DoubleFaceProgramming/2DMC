from ....src.world_gen import *
from ....src.constants import *
import pygame
from pygame.locals import *

WIDTH, HEIGHT = 64 * CHUNK_SIZE * BLOCK_SIZE, 128 * CHUNK_SIZE * BLOCK_SIZE

class Camera():
    def __init__(self):
        self.pos = VEC(0, 0)

for y in range(HEIGHT // CHUNK_SIZE // BLOCK_SIZE):
    for x in range(WIDTH // CHUNK_SIZE // BLOCK_SIZE):
        chunk = (x, y)
        Chunk.instances[chunk] = Chunk(chunk)

image = pygame.Surface((WIDTH, HEIGHT))
for chunk in Chunk.instances.values():
    chunk.draw(Camera(), image)

pygame.image.save(image, "img.png")