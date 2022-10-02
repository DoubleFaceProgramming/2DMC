# 2DMC is a passion project to recreate the game "Minecraft" (all credit to Mojang Studios) in 2D.
# Copyright (C) 2022 Doubleface
# You can view the terms of the GPL License in LICENSE.md

# The majority of the game assets are properties of Mojang Studios,
# you can view their TOS here: https://account.mojang.com/documents/minecraft_eula

from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING: # Type annotations without causing circular imports
    from src.management.game_manager import GameManager
    from src.world.block import Location

from math import floor, ceil
import pygame

from src.common.constants import CHUNK_SIZE, VEC, GRAVITY, BLOCK_SIZE, SCR_DIM, TERMINAL_VEL
from src.effects.spawn_particles import walk_particles, fall_particles
from src.management.sprite import Sprite, LayersEnum
from src.common.utils import sign, to_pps, to_bps
from src.entities.entity import Entity

from pygame.locals import (
    K_a, K_d, K_w, K_s, K_LEFT, K_RIGHT, K_UP, K_DOWN, K_SPACE
)

class Camera:
    """Class that represents the camera"""
    def __init__(self, manager: GameManager, player) -> None:
        self.manager = manager
        self.scene = self.manager.scene
        self.player = player
        self.pos = self.player.pos - VEC(SCR_DIM) / 2
        self.coords = (self.pos + (VEC(SCR_DIM) / 2 - self.player.size / 2)) // BLOCK_SIZE
        self.chunk_coords = self.coords // CHUNK_SIZE
        self.scalar = VEC(0.6, 1.2)

    def update(self) -> None:
        mpos = pygame.mouse.get_pos()

        # How much the player moved since last frame (relative to camera)
        tick_offset = self.player.pos - self.pos - (VEC(SCR_DIM) / 2 - self.player.size / 2)

        # Calculate the distance the mouse is from the center of the screen
        x_dist, y_dist = mpos[0] - SCR_DIM[0] / 2, mpos[1] - SCR_DIM[1] / 2

        # Squaring the distance so that the further out the cursor from the center, the camera moves exponentially away
        # Times a scalar so that the camera can move further in the y-direction but less in the x-direction
        dist_squared = VEC(
            sign(x_dist) * x_dist ** 2 * self.scalar.x,
            sign(y_dist) * y_dist ** 2 * self.scalar.y
        )

        # Combined the offset due to player movement and offset due to cursor, and scale it down to a reasonable value
        self.pos += (tick_offset * 2 + VEC(dist_squared) / 300) * self.manager.dt
        self.coords = (self.pos + (VEC(SCR_DIM) / 2 - self.player.size / 2)) // BLOCK_SIZE
        self.chunk_coords = self.coords // CHUNK_SIZE

class Player(Entity):
    """A sprite that represents the game's player """

    def __init__(self, manager: GameManager) -> None:
        super().__init__(VEC(0, -3) * BLOCK_SIZE, VEC(int(0.225 * BLOCK_SIZE), int(1.8 * BLOCK_SIZE)), manager, LayersEnum.PLAYER)
        self.camera = Camera(self.manager, self)
        self.slide = to_pps(26) # Speed of acceleration and deceleration
        self.speed = to_pps(5.6) # Max speed
        self.jump_vel = -537 # Velocity at start of jump
        self.on_ground = False
        self.start_fall = self.pos.y

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
        if (keys[K_UP] or keys[K_w] or keys[K_SPACE]) and self.on_ground:
            self.vel.y = self.jump_vel

        super().update_vel()

        self.detecting_locations: dict[tuple[int, int], Location] = {}
        self.update_pos_x()
        for y in range(int(self.coords.y - 1), int(self.coords.y + 3)):
            for x in range(int(self.coords.x - 1), int(self.coords.x + 2)):
                if not (location := self.scene.locations[(x, y)]): continue
                self.detecting_locations[(x, y)] = location
                # Creates a new rect where the width is increased by one which solves a rounding problem
                modified_rect = pygame.Rect(self.rect.left, self.rect.top, self.rect.width + 1, self.rect.height)
                if not modified_rect.colliderect(location.rect): continue
                if self.vel.x < 0:
                    self.set_pos(VEC(location.rect.right, self.pos.y))
                elif self.vel.x > 0:
                    self.set_pos(VEC(location.rect.left - self.size.x, self.pos.y))
                self.vel.x = 0

        self.on_ground = False
        self.update_pos_y()
        for location in self.detecting_locations.values():
            # Creates a new rect where the height is increased by one which solves a rounding problem
            modified_rect = pygame.Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height + 1)
            if not modified_rect.colliderect(location.rect): continue
            if self.vel.y < 0:
                self.set_pos(VEC(self.pos.x, location.rect.bottom))
            elif self.vel.y > 0:
                self.set_pos(VEC(self.pos.x, location.rect.top - self.size.y))
                self.on_ground = True
            self.vel.y = 0

        self.update_coords()
        self.camera.update()

        walk_particles(self.manager, self.scene.locations[self.coords + VEC(0, 2)])

        if self.on_ground:
            if self.pos.y - self.start_fall >= 4 * BLOCK_SIZE:
                fall_particles(self.manager, int((self.pos.y - self.start_fall) // BLOCK_SIZE), self.scene.locations[self.coords + VEC(0, 2)])
            self.start_fall = self.pos.y

    def draw(self) -> None:
        pygame.draw.rect(self.manager.screen, (255, 0, 0), (*(self.pos - self.camera.pos), *self.size))

    def debug(self) -> None:
        pass