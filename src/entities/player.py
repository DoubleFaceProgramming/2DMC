from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING: # Type annotations without causing circular imports
    from src.management.game_manager import GameManager

import pygame

from src.utils.constants import VEC, GRAVITY, BLOCK_SIZE
from src.management.sprite import Sprite, LayersEnum
from src.entities.entity import Entity

from pygame.locals import (
    K_a, K_d, K_w, K_LEFT, K_RIGHT, K_UP, K_SPACE
)

class Player(Entity):
    """A sprite that represents the game's player """

    def __init__(self, manager: GameManager) -> None:
        super().__init__(VEC(0, 3) * BLOCK_SIZE, VEC(0.225 * BLOCK_SIZE, 1.8 * BLOCK_SIZE), manager, LayersEnum.PLAYER)
        self.slide = 1200 # Speed of acceleration and deceleration
        self.speed = 250 # Max speed
        self.jump_vel = -800 # Velocity at start of jump

    def update(self) -> None:
        super().update()

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

    def draw(self) -> None:
        pygame.draw.rect(self.manager.screen, (255, 0, 0), (*self.pos, *self.size))

    def debug(self) -> None:
        pass