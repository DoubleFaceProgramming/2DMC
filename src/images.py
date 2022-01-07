import pygame
from pygame.locals import SRCALPHA, HWSURFACE, DOUBLEBUF
import os

from src.constants import *
from src.utils import pathof

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50, 50)
pygame.init()
pygame.display.set_mode((0, 0), HWSURFACE | DOUBLEBUF)

player_head_img = pygame.image.load(pathof("assets/textures/player/head.png")).convert()
player_body_img = pygame.image.load(pathof("assets/textures/player/body.png")).convert()
player_arm_img = pygame.image.load(pathof("assets/textures/player/arm.png")).convert()
player_leg_img = pygame.image.load(pathof("assets/textures/player/leg.png")).convert()
player_head_img = pygame.transform.scale(player_head_img, (28, 28))
player_body_img = pygame.transform.scale(player_body_img, (14, 43))
player_leg_img = pygame.transform.scale(player_leg_img, (14, 45))
player_arm_img = pygame.transform.scale(player_arm_img, (14, 43))
head_size = VEC(player_head_img.get_width()*2, player_head_img.get_height()*2)
body_size = VEC(player_body_img.get_width()*2, player_body_img.get_height()*2)
arm_size = VEC(player_arm_img.get_width()*2, player_arm_img.get_height()*2)
leg_size = VEC(player_leg_img.get_width()*2, player_leg_img.get_height()*2)
player_head = pygame.Surface(head_size, SRCALPHA)
player_body = pygame.Surface(body_size, SRCALPHA)
player_arm = pygame.Surface(arm_size, SRCALPHA)
player_leg = pygame.Surface(leg_size, SRCALPHA)
player_head.blit(player_head_img, (head_size/4+VEC(0, -8)))
player_body.blit(player_body_img, (body_size/4))
player_arm.blit(player_arm_img, (arm_size/2+VEC(-7, -6)))
player_leg.blit(player_leg_img, (leg_size/2+VEC(-7, -2)))
invert_player_head = pygame.transform.flip(player_head, True, False)
invert_player_body = pygame.transform.flip(player_body, True, False)
invert_player_arm = pygame.transform.flip(player_arm, True, False)
invert_player_leg = pygame.transform.flip(player_leg, True, False)

inventory_img = pygame.image.load(pathof("assets/textures/gui/inventory.png")).convert_alpha()
inventory_img = pygame.transform.scale(inventory_img, (int(inventory_img.get_width()*2.5), int(inventory_img.get_height()*2.5)))
hotbar_img = pygame.image.load(pathof("assets/textures/gui/hotbar.png")).convert_alpha()
hotbar_img = pygame.transform.scale(hotbar_img, (int(hotbar_img.get_width()*2.5), int(hotbar_img.get_height()*2.5)))
hotbar_selection_img = pygame.image.load(pathof("assets/textures/gui/hotbar_selection.png")).convert_alpha()
hotbar_selection_img = pygame.transform.scale(hotbar_selection_img, (int(hotbar_selection_img.get_width()*2.5), int(hotbar_selection_img.get_height()*2.5)))

block_textures = {}
for img in os.listdir(pathof("assets/textures/blocks/")):
    block_textures[img[:-4]] = pygame.image.load(os.path.join(pathof("assets/textures/blocks/"), img)).convert()
for image in block_textures:
    block_textures[image] = pygame.transform.scale(block_textures[image], (BLOCK_SIZE, BLOCK_SIZE))
    block_textures[image].set_colorkey((255, 255, 255))