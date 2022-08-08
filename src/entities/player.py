# 2DMC is a passion project to recreate the game "Minecraft" (all credit to Mojang Studios) in 2D.
# Copyright (C) 2022 Doubleface
# You can view the terms of the GPL License in LICENSE.md

# The majority of the game assets are properties of Mojang Studios,
# you can view their TOS here: https://account.mojang.com/documents/minecraft_eula

from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING: # Type annotations without causing circular imports
    from src.management.game_manager import GameManager

import pygame

from src.utils.constants import VEC, GRAVITY, BLOCK_SIZE, SCR_DIM
from src.management.sprite import Sprite, LayersEnum
from src.entities.entity import Entity
from src.utils.utils import sign

from pygame.locals import (
    K_a, K_d, K_w, K_LEFT, K_RIGHT, K_UP, K_SPACE
)

class Camera:
    """Class that represents the camera"""
    def __init__(self, player) -> None:
        self.player = player
        self.pos = self.player.size / 2
        self.pos = self.player.pos - self.pos - VEC(SCR_DIM) / 2 + self.player.size / 2
        self.scalar = VEC(0.6, 1.2)

    def update(self, dt: float) -> None:
        mpos = pygame.mouse.get_pos()

        # How much the player moved since last frame (relative to camera)
        tick_offset = self.player.pos - self.pos - (VEC(SCR_DIM) / 2 - self.player.size / 2)

        # Calculate the distance the mouse is from the center of the screen
        if not self.player.inventory.visible:
            x_dist, y_dist = mpos[0] - SCR_DIM[0] / 2, mpos[1] - SCR_DIM[1] / 2
        else: # (if the player is in their inventory)
            x_dist, y_dist = 0, 0

        # Squaring the distance so that the further out the cursor from the center, the camera moves exponentially away
        # Times a scalar so that the camera can move further in the y-direction but less in the x-direction
        dist_squared = VEC(
            sign(x_dist) * x_dist ** 2 * self.scalar.x,
            sign(y_dist) * y_dist ** 2 * self.scalar.y
        )

        # Combined the offset due to player movement and offset due to cursor, and scale it down to a reasonable value
        self.pos += (tick_offset * 2 + VEC(dist_squared) / 300) * dt

class Player(Entity):
    """A sprite that represents the game's player """

    def __init__(self, manager: GameManager) -> None:
        super().__init__(VEC(0, 3) * BLOCK_SIZE, VEC(0.225 * BLOCK_SIZE, 1.8 * BLOCK_SIZE), manager, LayersEnum.PLAYER)
        self.camera = Camera(self)
        self.slide = 1200 # Speed of acceleration and deceleration
        self.speed = 250 # Max speed
        self.jump_vel = -800 # Velocity at start of jump

    def update(self) -> None:
        keys = pygame.key.get_pressed()
        self.acc = VEC(0, GRAVITY)
        if keys[K_LEFT] or keys[K_a]:
            self.acc.x -= self.slide # Accelerate
        elif self.vel.x < 0:
            self.acc.x += self.slide # Decelerate
        if keys[K_RIGHT] or keys[K_d]:
            self.acc.x += self.slide # Accelerate
        elif self.vel.x > 0:
            self.acc.x -= self.slide # Decelerate
        # if (keys[K_UP] or keys[K_w] or keys[K_SPACE]) and self.on_ground:
        #     self.vel.y = self.jump_vel

        super().update()

    def draw(self) -> None:
        pygame.draw.rect(self.manager.screen, (255, 0, 0), (*(self.pos - self.camera.pos), *self.size))

    def debug(self) -> None:
        pass