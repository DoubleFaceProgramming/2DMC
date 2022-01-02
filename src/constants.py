from random import randint
from win32api import EnumDisplayDevices, EnumDisplaySettings
from pygame.font import Font, init
from pygame.math import Vector2

init()

WIDTH, HEIGHT = 1200, 600
SCR_DIM = (WIDTH, HEIGHT)
GRAVITY = 0.5
SLIDE = 0.3
TERMINAL_VEL = 24
BLOCK_SIZE = 64
CHUNK_SIZE = 8
SEED = randint(-2147483648, 2147483647)

FPS = getattr(EnumDisplaySettings(EnumDisplayDevices().DeviceName, -1), "DisplayFrequency")
REGULAR_FONT_LOC = "assets/fonts/regular.ttf"
FONT24 = Font(REGULAR_FONT_LOC, 24)
FONT20 = Font(REGULAR_FONT_LOC, 20)
VEC = Vector2