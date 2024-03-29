# 2DMC is a passion project to recreate the game "Minecraft" (all credit to Mojang Studios) in 2D.
# Copyright (C) 2022 Doubleface
# You can view the terms of the GPL License in LICENSE.md

# The majority of the game assets are properties of Mojang Studios,
# you can view their TOS here: https://account.mojang.com/documents/minecraft_eula

from pygame.font import Font, init
from pygame.math import Vector2
from pygame import USEREVENT
from enum import Enum, auto
from random import randint

from src.parsing import load_block_data, load_ore_distribution, load_structures
import dist.exe_comp as exe

init()

WIDTH, HEIGHT = SCR_DIM = 1200, 600
BLUE_SKY = (135, 206, 250)
MAX_Y = 1024
GRAVITY = 28
SPACING = 24
TERMINAL_VEL = 24
MIN_BLOCK_SIZE = 16
BLOCK_SIZE = 64
CHUNK_SIZE = 8
CAVE_PREGEN_BATCH = 4

# Universal seed for profiling/timing: 50687767
# Seeds for structure gen testing: -1797233725, -301804449, 1666679850, 1671665804
# Seed for low world gen (loads at 1056) testing: 1561761502
SEED = randint(-2147483648, 2147483647)

FPS = float("inf")
VEC = Vector2

REGULAR_FONT_LOC = exe.pathof("assets/fonts/regular.ttf")
PROFILE_DIR = exe.pathof("build/profiles/")
SCREENSHOTS_DIR = exe.pathof("screenshots/")
FONT24 = Font(REGULAR_FONT_LOC, 24)
FONT20 = Font(REGULAR_FONT_LOC, 20)
FONT10 = Font(REGULAR_FONT_LOC, 10)

BLOCK_DATA = load_block_data()
STRUCTURES = load_structures()
ORE_DISTRIBUTION = load_ore_distribution()

CONFLICTING_STRUCTURES = {
    ("oak_tree", ): ["tall_grass"],
    ("granite", "diorite", "andesite"): ["coal_ore", "iron_ore", "lapis_ore", "gold_ore", "redstone_ore", "diamond_ore", "emerald_ore"],
    ("tuff", ): ["deepslate_coal_ore", "deepslate_iron_ore", "deepslate_lapis_ore", "deepslate_gold_ore", "deepslate_redstone_ore", "deepslate_diamond_ore", "deepslate_emerald_ore"]
}
MAX_STRUCTURE_SIZE = (2, 2)

# We dont need this yet but if we ever need custom events I realised we could do something like this :P
class CustomEvents(Enum):
    pass
    # AN_EVENT = USEREVENT + auto()
    # ANOTHER_EVENT = USEREVENT + auto()
    # . . . ect
    
class Anchors(Enum):
    TOP = (0, -1)
    BOTTOM = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    CENTER = (0, 0)
    TOPLEFT = (-1, -1)
    TOPRIGHT = (1, -1)
    BOTTOMLEFT = (-1, 1)
    BOTTOMRIGHT = (1, 1)

import src.game as game
MANAGER = game.GameManager()
