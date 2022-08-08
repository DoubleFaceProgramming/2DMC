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
        self.coords = self.pos // BLOCK_SIZE

    def update(self) -> None:
        # THIS CODE HAS BEEN COPY PASTED. IDK IF THIS IS RIGHT OR NOT BUT IM TOO SMOL BRAIN TO UNDERSTAND AND CHECK MYSELF D:

        self.vel += self.acc * self.manager.dt # Accelerate velocity
        self.vel.x = clamp(self.vel.x, -self.speed, self.speed)[0] # Clamp x to max speed
        self.vel.x = snap(self.vel.x, 0, self.acc.x * self.manager.dt) # Snap x to 0 if it gets close (prevents tiny movement after acceleration)

        self.pos += self.vel * self.manager.dt # Move position by velocity
        # Clamps position to inside the window, also gets the direction of clamping
        self.pos, clamp_direction = clamp(self.pos, VEC(0, 0), VEC(WIDTH, HEIGHT) - self.size)
        # If the bottom y was clamped, the player is on ground, if not, the player is NOT on ground
        self.on_ground = clamp_direction.y == 1
        # If player is on ground, reset y velocity, doesn't make a difference here but future proofing
        self.vel.y = 0 if self.on_ground else self.vel.y
        # If the player touches the wall reset acceleration, so that when player turns immediately there wouldn't be a smol delay
        self.vel.x = 0 if clamp_direction.x else self.vel.x

    def draw(self):
        pass