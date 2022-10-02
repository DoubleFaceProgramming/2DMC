from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING: # Type annotations without causing circular imports
    from src.management.game_manager import GameManager

from src.common.utils import WorldSlices, sign, to_pps, filled_surf
from src.common.constants import VEC, BLOCK_SIZE, GRAVITY
from src.management.sprite import LayersEnum, Sprite
from src.world.block import Location, Block
from src.common.images import missing
from random import randint, uniform
from pygame import Surface, Rect
from math import floor, ceil
import pygame
import time

class Particle(Sprite):
    instances: list[Particle] = []

    def __init__(self, manager: GameManager, pos: tuple[int, int], image: Surface, layer: LayersEnum=LayersEnum.REG_PARTICLES):
        super().__init__(manager, layer)
        __class__.instances.append(self)

        self.pos = VEC(pos)
        self.coords = self.pos // BLOCK_SIZE
        self.vel = VEC(0, 0)
        self.image = image
        self.size = VEC(self.image.get_size())
        self.survive_time = float("inf")
        self.start_time = time.time()

    def update(self):
        if time.time() - self.start_time > self.survive_time:
            self.kill()
        self.pos += self.vel * self.manager.dt
        self.coords = VEC((floor if self.pos.x > 0 else ceil)(self.pos.x) // BLOCK_SIZE, (floor if self.pos.y > 0 else ceil)(self.pos.y) // BLOCK_SIZE)

    def draw(self):
        self.manager.screen.blit(self.image, self.pos - self.size // 2 - self.manager.scene.player.camera.pos)

class PhysicsParticle(Particle):
    def __init__(self, manager: GameManager, pos: tuple[int, int], image: Surface, worldslice: WorldSlices):
        super().__init__(manager, pos, image)
        self.worldslice = worldslice

    def update(self) -> None:
        self.move()

        # Collision with the blocks around, block on the left if going left, block below if moving down, and vice versa
        for pos in set([(self.coords.x + sign(self.vel.x), self.coords.y), (self.coords.x, self.coords.y + sign(self.vel.y))]):
            if pos in Location.instances and Location.instances[pos][self.worldslice]:
                loc = Location.instances[pos]
                # TODO: Use tags here, for blocks with collision (if loc[1] (middleground) has collision)
                location_rect = pygame.Rect(loc.coords.x * BLOCK_SIZE, loc.coords.y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                if self.vel.x != 0:
                    if location_rect.collidepoint(self.pos.x + self.vel.x * self.manager.dt, self.pos.y):
                        self.vel.x = 0
                        break
                if self.vel.y != 0:
                    if location_rect.collidepoint(self.pos.x, self.pos.y + self.vel.y * self.manager.dt):
                        self.vel.y = 0
                        break

        super().update()

    def move(self) -> None:
        # Fall
        self.vel.y += GRAVITY * self.manager.dt
        # X-velocity gets decreased over time
        self.vel.x -= self.vel.x * 6 * self.manager.dt

class BlockParticle(PhysicsParticle):
    def __init__(self, manager: GameManager, pos: tuple[int, int], block: Block, subsurface: Rect = Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE), vel_range: tuple[tuple[float, float], tuple[float, float]] = ((-1.5, 1.5), (-3, 0.5))):
        sub = block.image.subsurface(subsurface)
        color = sub.get_at((randint(0, sub.get_width() - 1), randint(0, sub.get_height() - 1)))
        image = filled_surf((s := randint(6, 8), s), color, 0)

        super().__init__(manager, pos, image, block.worldslice)
        self.vel = VEC(to_pps(uniform(*vel_range[0])), to_pps(uniform(*vel_range[1])))
        self.survive_time = uniform(0.3, 0.6)
