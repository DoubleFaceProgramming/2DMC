from pygame.locals import *
from pathlib import Path
from random import *
import pygame
import time
import sys
import os

SIZE = 512
BLOCK_SIZE = 16
CHUNK_SIZE = 8
NUM_OF_CHUNKS = SIZE // (CHUNK_SIZE * BLOCK_SIZE)
NUM_OF_BLOCKS = SIZE // BLOCK_SIZE + 1

pygame.init()
screen = pygame.display.set_mode((SIZE, SIZE), HWSURFACE | DOUBLEBUF)
pygame.display.set_caption(f"TEST")
clock = pygame.time.Clock()
segmented = True

BLOCK_TEXTURES = {}
for img in os.listdir("assets/textures/blocks/"):
    BLOCK_TEXTURES[Path(img).stem] = pygame.image.load(os.path.join("assets/textures/blocks/", img)).convert()
for image in BLOCK_TEXTURES:
    BLOCK_TEXTURES[image] = pygame.transform.scale(BLOCK_TEXTURES[image], (BLOCK_SIZE, BLOCK_SIZE))
    BLOCK_TEXTURES[image].set_colorkey((255, 255, 255))

# Pre-generate what each block would be
all_blocks = []
for y in range(NUM_OF_BLOCKS):
    all_blocks.append([])
    for x in range(NUM_OF_BLOCKS):
        # Choose a random block from the block textures
        all_blocks[y].append(choice(list(BLOCK_TEXTURES.values())))

chunk_surfs = []
# Loop through each line of chunks
for cy in range(NUM_OF_CHUNKS):
    # Add a line
    chunk_surfs.append([])
    # Loop through each chunk in a line
    for cx in range(NUM_OF_CHUNKS):
        # Create a surface for the chunk
        surf = pygame.Surface((CHUNK_SIZE * BLOCK_SIZE, CHUNK_SIZE * BLOCK_SIZE), SRCALPHA)
        # Loop through every line of blocks of the chunk
        for by in range(CHUNK_SIZE):
            # Loop through ever block in the line
            for bx in range(CHUNK_SIZE):
                # Blit the block at the corresponding location onto the chunk
                surf.blit(all_blocks[cy * CHUNK_SIZE + by][cx * CHUNK_SIZE + bx], (bx * BLOCK_SIZE, by * BLOCK_SIZE))
        # Add that chunk surface to the list
        chunk_surfs[cy].append(surf)

avg_fps = 0
fps_timer = time.time()
running = True
while running:
    avg_fps = (avg_fps + round(clock.get_fps())) // 2 // 50 * 50
    if time.time() - fps_timer > 0.5:
        pygame.display.set_caption(f"TEST | Mode: {'Per-chunk' if segmented == True else 'Per-block'} | FPS: {avg_fps}")
        fps_timer = time.time()
    screen.fill((135, 206, 250))

    if not segmented:
        # Loop through every pre-generated block and blit them one by one
        for y, line in enumerate(all_blocks):
            for x, block in enumerate(line):
                screen.blit(block, (x * BLOCK_SIZE, y * BLOCK_SIZE))
    else:
        # Loop through every chunk and blit the surface containing all the blocks in it
        for y, line in enumerate(chunk_surfs):
            for x, chunk in enumerate(line):
                screen.blit(chunk, (x * CHUNK_SIZE * BLOCK_SIZE, y * CHUNK_SIZE * BLOCK_SIZE))

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                segmented = not segmented

    clock.tick_busy_loop(3000)
    pygame.display.flip()

pygame.quit()
sys.exit()