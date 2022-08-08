from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING: # Type annotations without causing circular imports
    from src.management.game_manager import GameManager

import pygame

from src.utils.constants import VEC, BLOCK_SIZE, WIDTH, HEIGHT
from src.management.sprite import LayersEnum, Sprite
from src.utils.clamps import clamp, snap

class Entity(Sprite):
    def __init__(self, pos, size, manager: GameManager, layer: int | LayersEnum | None = None, debug_layer: int | LayersEnum | None = None) -> None:
        super().__init__(manager, layer or LayersEnum.ENTITIES, debug_layer)
        self.size = VEC(size)
        self.pos = VEC(pos)
        self.vel = VEC(0, 0)
        self.acc = VEC(0, 0)
        self.rect = pygame.Rect(pos, size)
        self.image = pygame.Surface((0, 0))
        self.coords = self.pos // BLOCK_SIZE

    def update(self) -> None:
        self.vel += self.acc * self.manager.dt                         # Accelerate velocity
        self.vel.x, _ = clamp(self.vel.x, -self.speed, self.speed)     # Clamp x to max speed
        self.vel.x = snap(self.vel.x, 0, self.acc.x * self.manager.dt) # Snap x to 0 if it gets close (prevents tiny movement after acceleration)

        # Move position by velocity
        self.pos += self.vel * self.manager.dt
        # Clamps position to inside the window, also gets the direction of clamping
        self.pos, _ = clamp(self.pos, VEC(0, 0), VEC(WIDTH, HEIGHT) - self.size + (1, 1))

    def draw(self):
        self.manager.screen.blit(self.image, self.pos - self.scene.player.camera.offset)