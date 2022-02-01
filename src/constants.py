from pygame.font import Font, init
from pygame.math import Vector2
from random import randint

from src.parsing import load_block_data, load_ore_distribution, load_structures
import build.exe_comp as exe

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

REGULAR_FONT_LOC = exe.pathof("assets/fonts/regular.ttf")
PROFILE_DIR = exe.pathof("build\\profiles\\")
FONT24 = Font(REGULAR_FONT_LOC, 24)
FONT20 = Font(REGULAR_FONT_LOC, 20)

BLOCK_DATA = load_block_data()
STRUCTURES = load_structures()
ORE_DISTRIBUTION = load_ore_distribution()
print(ORE_DISTRIBUTION)

CONFLICTING_STRUCTURES = {
    ("oak_tree", ): ["tall_grass"],
    ("granite", "diorite", "andesite"): ["coal_ore", "iron_ore", "lapis_ore", "gold_ore", "redstone_ore", "diamond_ore", "emerald_ore"],
    ("tuff", ): ["deepslate_coal_ore", "deepslate_iron_ore", "deepslate_lapis_ore", "deepslate_gold_ore", "deepslate_redstone_ore", "deepslate_diamond_ore", "deepslate_emerald_ore"]
}