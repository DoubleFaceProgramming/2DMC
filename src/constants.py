from pygame.font import Font, init
from pygame.math import Vector2
from random import randint
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

# Seed for structure gen testing: -1797233725
# Seed for low world gen (loads at 1056) testing: 1561761502
SEED = randint(-2147483648, 2147483647)

FPS = 1000
VEC = Vector2

BUNDLE_DIR = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
REGULAR_FONT_LOC = os.path.abspath(os.path.join(BUNDLE_DIR, "assets/fonts/regular.ttf"))
if not os.path.exists(REGULAR_FONT_LOC):
    REGULAR_FONT_LOC = os.path.abspath(os.path.join(BUNDLE_DIR, "../assets/fonts/regular.ttf"))
PROFILE_DIR = "build\profiles\\"
FONT24 = Font(REGULAR_FONT_LOC, 24)
FONT20 = Font(REGULAR_FONT_LOC, 20)

CONFLICTING_STRUCTURES = {
    ("oak_tree", ): ["tall_grass"],
    ("granite", "diorite", "andesite"): ["coal_ore", "iron_ore", "lapis_ore", "gold_ore", "redstone_ore", "diamond_ore", "emerald_ore"],
    ("tuff", ): ["deepslate_coal_ore", "deepslate_iron_ore", "deepslate_lapis_ore", "deepslate_gold_ore", "deepslate_redstone_ore", "deepslate_diamond_ore", "deepslate_emerald_ore"]
}