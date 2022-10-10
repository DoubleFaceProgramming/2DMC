# 2DMC is a passion project to recreate the game "Minecraft" (all credit to Mojang Studios) in 2D.
# Copyright (C) 2022 Doubleface
# You can view the terms of the GPL License in LICENSE.md

# The majority of the game assets are properties of Mojang Studios,
# you can view their TOS here: https://account.mojang.com/documents/minecraft_eula

from pygame.math import Vector2 as VEC
from build.exe_comp import pathof

WIDTH, HEIGHT = SCR_DIM = 1200, 600
BLUE_SKY = (135, 206, 250)
TERMINAL_VEL = 1000
BLOCK_SIZE = 64
CHUNK_SIZE = 8
CHUNK_PIXEL_SIZE = CHUNK_SIZE * BLOCK_SIZE
GRAVITY = 1800
DEBUG_SPACING = 24
MAX_Y = 1024

PROFILES = pathof("dev/profiles/")
ASSETS = pathof("assets")