# 2DMC is a passion project to recreate the game "Minecraft" (all credit to Mojang Studios) in 2D.
# Copyright (C) 2022 Doubleface
# You can view the terms of the GPL License in LICENSE.md

# The majority of the game assets are properties of Mojang Studios,
# you can view their TOS here: https://account.mojang.com/documents/minecraft_eula

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING: # Type annotations without causing circular imports
    from src.management.game_manager import GameManager

from math import floor, ceil
import pygame

from src.common.constants import TERMINAL_VEL, VEC, BLOCK_SIZE, CHUNK_SIZE
from src.management.sprite import LayersEnum, Sprite
from src.common.clamps import clamp, snap, clamp_max
from src.common.utils import sign

class Entity(Sprite):
    def __init__(self, pos, size, manager: GameManager, layer: int | LayersEnum | None = None, debug_layer: int | LayersEnum | None = None) -> None:
        super().__init__(manager, layer or LayersEnum.ENTITIES, debug_layer)
        self.size = VEC(size)
        self.pos = VEC(pos)
        self.vel = VEC(0, 0)
        self.acc = VEC(0, 0)
        self.rect = pygame.Rect(self.pos, self.size)
        self.image = pygame.Surface((0, 0))
        self.coords = self.pos // BLOCK_SIZE
        self.chunk_coords = self.coords // CHUNK_SIZE
        self.detecting_rects = {}

    def update_vel(self) -> None:
        self.vel += self.acc * self.manager.dt                         # Accelerate velocity
        self.vel.x, _ = clamp(self.vel.x, -self.speed, self.speed)     # Clamp x to max speed
        self.vel.x = snap(self.vel.x, 0, self.acc.x * self.manager.dt) # Snap x to 0 if it gets close (prevents tiny movement after acceleration)
        self.vel.y, _ = clamp_max(self.vel.y, TERMINAL_VEL)

    def update_pos_x(self) -> None:
        self.pos.x += self.vel.x * self.manager.dt
        self.rect.left = floor(self.pos.x)

    def update_pos_y(self) -> None:
        self.pos.y += self.vel.y * self.manager.dt
        self.rect.top = floor(self.pos.y)

    def update_pos_x_fake(self) -> pygame.Rect:
        fake_pos = self.pos.copy()
        fake_pos.x += ceil(self.vel.x * self.manager.dt)
        fake_rect = self.rect.copy()
        fake_rect.left = floor(fake_pos.x) + sign(self.vel.x)
        return fake_rect

    def update_pos_y_fake(self) -> pygame.Rect:
        fake_pos = self.pos.copy()
        fake_pos.y += ceil(self.vel.y * self.manager.dt)
        fake_rect = self.rect.copy()
        fake_rect.top = floor(fake_pos.y) + sign(self.vel.y)
        return fake_rect

    def update_coords(self) -> None:
        self.coords = self.pos // BLOCK_SIZE
        self.chunk_coords = self.coords // CHUNK_SIZE

    def set_pos(self, new: VEC) -> None:
        self.pos = new
        self.rect.topleft = self.pos

    def change_pos(self, dp: VEC) -> None:
        self.pos += dp
        self.rect.topleft = self.pos

    def update(self) -> None:
        self.update_vel()
        self.update_pos_x()
        self.update_pos_y()
        self.update_coords()

    def draw(self):
        self.manager.screen.blit(self.image, self.pos - self.scene.player.camera.pos)