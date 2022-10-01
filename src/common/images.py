# 2DMC is a passion project to recreate the game "Minecraft" (all credit to Mojang Studios) in 2D.
# Copyright (C) 2022 Doubleface
# You can view the terms of the GPL License in LICENSE.md

# The majority of the game assets are properties of Mojang Studios,
# you can view their TOS here: https://account.mojang.com/documents/minecraft_eula

from pygame.locals import SRCALPHA, HWSURFACE, DOUBLEBUF
from pygame.transform import scale
from pygame.image import load
from pathlib import Path
from os.path import join
import pygame
import os

from src.common.constants import VEC, BLOCK_SIZE, ASSETS
from src.common.utils import scale_by
from build.exe_comp import pathof

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50, 50)
pygame.init()
pygame.display.set_mode((0, 0), HWSURFACE | DOUBLEBUF)

missing = pygame.image.load(pathof("assets/misc/missing.png"))
window_icon = pygame.image.load(pathof("assets/logo.png"))

# Simple load functions
player = lambda texture: join(ASSETS, "textures", "player", (texture + ".png"))
gui = lambda texture: join(ASSETS, "textures", "gui", (texture + ".png"))

# Load
player_head_img = scale_by(load(player("head")), 3.5).convert()
player_body_img = scale_by(load(player("body")), 3.5).convert()
player_arm_img  = scale_by(load(player("arm")),  3.5).convert()
player_leg_img  = scale_by(load(player("leg")),  3.5).convert()

# Size
head_size = VEC(player_head_img.get_size()) * 2
body_size = VEC(player_body_img.get_size()) * 2
arm_size  = VEC(player_arm_img.get_size())  * 2
leg_size  = VEC(player_leg_img.get_size())  * 2

# Surfaces
player_head = pygame.Surface(head_size, SRCALPHA)
player_body = pygame.Surface(body_size, SRCALPHA)
player_arm  = pygame.Surface(arm_size,  SRCALPHA)
player_leg  = pygame.Surface(leg_size,  SRCALPHA)

# head_size / 4 will equal half the size of player_head_img as head_size is 2x the size of the image
# thus head_size / 4 will place the head in the center of the surface (player_head)
# + VEC(0, -8) translates the image upwards by 8 pixels, which is about less than 1/3 of the head size (28)
# This will place the bottom part of the head in the center of the surface,
# thus when the surface rotates, the head will appear to rotate around the center
# A similar process is followed for the other images
player_head.blit(player_head_img, (head_size / 4 + VEC(0, -8)))
player_body.blit(player_body_img, (body_size / 4))
player_arm .blit(player_arm_img,  (arm_size  / 2 + VEC(-7, -6)))
player_leg .blit(player_leg_img,  (leg_size  / 2 + VEC(-7, -2)))

invert_player_head = pygame.transform.flip(player_head, True, False)
invert_player_body = pygame.transform.flip(player_body, True, False)
invert_player_arm  = pygame.transform.flip(player_arm,  True, False)
invert_player_leg  = pygame.transform.flip(player_leg,  True, False)

# Load gui images
inventory_img = scale_by(load(gui("inventory")), 2.5).convert_alpha()
hotbar_img = scale_by(load(gui("hotbar")), 2.5).convert_alpha()
hotbar_selection_img = scale_by(load(gui("hotbar_selection")), 2.5).convert_alpha()

block_path = join(ASSETS, "textures", "blocks")
BLOCK_TEXTURES = {}
for img in os.listdir(block_path):
    BLOCK_TEXTURES[(key := Path(img).stem)] = scale(load(join(block_path, img)), (BLOCK_SIZE, BLOCK_SIZE)).convert()
    BLOCK_TEXTURES[key].set_colorkey((255, 255, 255))