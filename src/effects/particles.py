from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING: # Type annotations without causing circular imports
    from src.management.game_manager import GameManager

from src.common.constants import VEC, BLOCK_SIZE, GRAVITY
from src.common.utils import WorldSlices, sign, to_pps
from src.management.sprite import LayersEnum, Sprite
from src.world.block import Location, Block
from src.common.images import missing
from random import randint, uniform
from math import floor, ceil
from pygame import Surface
import pygame
import time

class Particle(Sprite):
    instances: list[Particle] = []

    def __init__(self, manager: GameManager, pos: tuple[int, int], vel: tuple[float, float], size: tuple[int, int], survive_time: float, layer: LayersEnum=LayersEnum.REG_PARTICLES):
        super().__init__(manager, layer)
        __class__.instances.append(self)

        self.pos = VEC(pos)
        self.coords = self.pos // BLOCK_SIZE
        self.vel = VEC(vel)
        self.size = size
        self.image = Surface(size)
        self.image.blit(pygame.transform.scale(missing, self.size), (0, 0))
        self.survive_time = survive_time
        self.start_time = time.time()

    def update(self):
        if time.time() - self.start_time > self.survive_time:
            self.kill()
        self.pos += self.vel * self.manager.dt
        self.coords = VEC((floor if self.pos.x > 0 else ceil)(self.pos.x) // BLOCK_SIZE, (floor if self.pos.y > 0 else ceil)(self.pos.y) // BLOCK_SIZE)

    def draw(self):
        self.manager.screen.blit(self.image, self.pos - self.manager.scene.player.camera.pos)

class PhysicsParticle(Particle):
    def __init__(self, manager: GameManager, pos: tuple[int, int], vel: tuple[int, int], size: tuple[int, int], survive_time: float, worldslice: WorldSlices):
        super().__init__(manager, pos, vel, size, survive_time)
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
        self.vel.x -= self.vel.x * 5 * self.manager.dt

class BlockParticle(PhysicsParticle):
    def __init__(self, manager, pos: tuple[int, int], block: Block):
        size = randint(6, 8)
        vel = to_pps(uniform(-1.5, 1.5)), to_pps(uniform(-3, 0.5))
        survive_time = uniform(0.3, 0.6)
        super().__init__(manager, pos, vel, (size, size), survive_time, block.worldslice)

        color = block.image.get_at((randint(0, block.image.get_width() - 1), randint(0, block.image.get_height() - 1)))
        self.image.fill(color)

    @classmethod
    def spawn(cls, manager: GameManager, loc: Location, ws: WorldSlices):
        spawn_range = ((loc.coords.x * BLOCK_SIZE, (loc.coords.x + 1) * BLOCK_SIZE),
                       (loc.coords.y * BLOCK_SIZE, (loc.coords.y + 1) * BLOCK_SIZE))
        for _ in range(randint(18, 26)):
            spawn_pos = (randint(*spawn_range[0]), randint(*spawn_range[1]))
            BlockParticle(manager, spawn_pos, loc[ws])
