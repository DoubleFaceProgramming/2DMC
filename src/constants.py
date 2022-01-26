from random import randint
from win32api import EnumDisplayDevices, EnumDisplaySettings
from pygame.font import Font, init
from pygame.math import Vector2
import sys
import os

init()

WIDTH, HEIGHT = 1200, 600
SCR_DIM = (WIDTH, HEIGHT)
GRAVITY = 0.5
SLIDE = 0.3
SPACING = 24
TERMINAL_VEL = 24
BLOCK_SIZE = 64
CHUNK_SIZE = 8
SEED = randint(-2147483648, 2147483647)

FPS = getattr(EnumDisplaySettings(EnumDisplayDevices().DeviceName, -1), "DisplayFrequency")
VEC = Vector2

BUNDLE_DIR = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
REGULAR_FONT_LOC = os.path.abspath(os.path.join(BUNDLE_DIR, "assets/fonts/regular.ttf"))
if not os.path.exists(REGULAR_FONT_LOC):
    REGULAR_FONT_LOC = os.path.abspath(os.path.join(BUNDLE_DIR, "../assets/fonts/regular.ttf"))
FONT24 = Font(REGULAR_FONT_LOC, 24)
FONT20 = Font(REGULAR_FONT_LOC, 20)

STRUCTURE_SEQUENCE = [
    "oak_tree",
    "tall_grass",
    "coal_ore",
    "iron_ore",
    "gold_ore",
    "lapis_lazuli_ore",
    "redstone_ore",
    "diamond_ore",
    "emerald_ore",
    "granite",
    "diorite",
    "andesite"
]
STRUCTURE_SEQUENCE_DICT = {struct : i for i, struct in enumerate(STRUCTURE_SEQUENCE)}