from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING: # Type annotations without causing circular imports
    from src.management.game_manager import GameManager

from src.utils.constants import VEC, BLOCK_SIZE, SCR_DIM
from src.management.sprite import LayersEnum, Sprite
from src.world.block import Location, Block
from src.utils.utils import WorldSlices
from src.utils.images import missing
from pygame import Surface
from random import randint
import pygame

class Particle(Sprite):
    instances: list[Particle] = []

    def __init__(self, manager: GameManager, pos: tuple[int, int], size: tuple[int, int], layer: LayersEnum=LayersEnum.REG_PARTICLES):
        super().__init__(manager, layer)
        __class__.instances.append(self)

        self.pos = VEC(pos)
        self.coords = self.pos // BLOCK_SIZE
        self.size = size
        self.image = Surface(size)
        self.image.blit(pygame.transform.scale(missing, self.size), (0, 0))

    def draw(self):
        self.manager.screen.blit(self.image, self.pos)

class PhysicsParticle(Particle):
    def __init__(self, manager: GameManager, pos: tuple[int, int], size: tuple[int, int]):
        super().__init__(manager, pos, size)

    # Add in the physics stuff in here :)

class BlockParticle(PhysicsParticle):
    def __init__(self, manager, pos, block: Block):
        if not block:
            return # Is this okay? This seems like it isnt okay but I... think its okay?

        size = randint(6, 8)
        super().__init__(manager, pos, (size, size))

        colour = block.image.get_at((randint(0, block.image.get_width() - 1), randint(0, block.image.get_height() - 1)))
        self.image.fill(colour)

    @classmethod
    def spawn(cls, manager: GameManager, loc: Location, ws: WorldSlice):
        BlockParticle(manager, (randint(0, SCR_DIM[0]), randint(0, SCR_DIM[1])), loc[ws])
