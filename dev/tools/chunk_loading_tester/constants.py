from pygame.math import Vector2
from pygame.locals import *

VEC = Vector2
FPS = 144
WIDTH, HEIGHT = 1280, 768
BG_COLOR = (135, 206, 250)
BLOCK_SIZE = 16 # Number of pixels in a block
CHUNK_SIZE = 8 # Number of blocks in a chunk
CHUNK_PIXEL_SIZE = BLOCK_SIZE * CHUNK_SIZE # Size in pixels of a chunk
SEED = 1