from random import randint
from win32api import EnumDisplayDevices, EnumDisplaySettings
from pygame.font import Font, init
from pygame.math import Vector2
import sys
import os

init()

WIDTH, HEIGHT = SCR_DIM = 1200, 600
BLUE_SKY = (135, 206, 250)
MAX_Y = 1024
GRAVITY = 0.5
SLIDE = 0.3
SPACING = 24
TERMINAL_VEL = 24
BLOCK_SIZE = 64
CHUNK_SIZE = 8
SEED = -1797233725#-643111093#randint(-2147483648, 2147483647) # Seed for structure gen testing: -1797233725

FPS = getattr(EnumDisplaySettings(EnumDisplayDevices().DeviceName, -1), "DisplayFrequency")
VEC = Vector2

BUNDLE_DIR = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
REGULAR_FONT_LOC = os.path.abspath(os.path.join(BUNDLE_DIR, "assets/fonts/regular.ttf"))
if not os.path.exists(REGULAR_FONT_LOC):
    REGULAR_FONT_LOC = os.path.abspath(os.path.join(BUNDLE_DIR, "../assets/fonts/regular.ttf"))
FONT24 = Font(REGULAR_FONT_LOC, 24)
FONT20 = Font(REGULAR_FONT_LOC, 20)

CONFLICTING_STRUCTURES = {
    ("oak_tree",): ["tall_grass"], 
    ("granite", "diorite", "andesite"): ["coal_ore", "iron_ore", "lapis_lazuli_ore", "gold_ore", "redstone_ore", "diamond_ore", "emerald_ore"]
}