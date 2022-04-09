from __future__ import annotations
from math import ceil, floor

from pygame import Color, Surface
from random import randint, choices
from typing import TYPE_CHECKING
import pygame
import time

from src.constants import MIN_BLOCK_SIZE, VEC, BLOCK_SIZE, GRAVITY, WIDTH, HEIGHT, MAX_Y
from src.sprite import LayerNotFoundException, LayersEnum, Sprite, SpriteNotFoundException
from src.utils import pps, inttup, sign

if TYPE_CHECKING:
    from src.block import Block

class Particle(Sprite):
    """A Common superclass for all particles"""
    instances = [] # List containing every particle, regardless of type

    def __init__(self, pos: tuple, vel: tuple, survive_time: float, image: Surface, layer: LayersEnum, master=None) -> None:
        super().__init__(layer)
        __class__.instances.append(self)
        self.world_pos = VEC(pos)
        self.pos = self.world_pos
        self.vel = pps(VEC(vel))
        self.coords = self.world_pos // BLOCK_SIZE
        self.survive_time = survive_time
        self.image = image
        # Set the time which the particle is going to last for
        self.start_time = time.time()
        self.master = master

    def update(self, dt: float, **kwargs) -> None:
        # If the particle's lifetime is greater than its intended lifetime, commit die
        if time.time() - self.start_time > self.survive_time:
            self.kill()

        self.world_pos += self.vel * dt
        self.pos = self.world_pos - kwargs["camera"].pos
        self.coords = VEC((floor if self.world_pos.x > 0 else ceil)(self.world_pos.x) // BLOCK_SIZE, (floor if self.world_pos.y > 0 else ceil)(self.world_pos.y) // BLOCK_SIZE)

    def draw(self, screen: Surface, **kwargs):
        screen.blit(self.image, (self.pos - VEC(self.image.get_size()) / 2))

    def kill(self) -> None:
        # There is a rare bug where the particle is killed twice,
        # therefore it is being removed from the list twice, so we catch that here
        try:
            super().kill()
        except (SpriteNotFoundException, LayerNotFoundException):
            pass

        try:
            __class__.instances.remove(self)
            del self
        except ValueError:
            pass

class GradualSpawningParticle:
    timer = time.time()
    
    @classmethod
    def spawn(cls, condition, frequency, *args, **kwargs):
        if condition:
            if (elapsed_time := time.time() - __class__.timer) >= frequency:
                __class__.timer = time.time()
                # If the loop took longer than 1 * spawn_frequency,
                # spawn multiple particles determined by elapsed_time / spawn_frequency
                for _ in range(round(elapsed_time / frequency)):
                    cls(*args, **kwargs)
        else:
            __class__.timer = time.time()

class PhysicsParticle(Particle):
    """A superclass for all particles that have gravity / collision"""

    def __init__(self, pos: tuple, vel: tuple, survive_time: float, image: Surface, blocks: dict, layer: LayersEnum, master=None) -> None:
        self.blocks = blocks
        super().__init__(pos, vel, survive_time, image, layer, master)

    def update(self, dt: float, **kwargs) -> None:
        self.move(dt)

        # Collision with the blocks around, block on the left if going left, block below if moving down, and vice versa
        for pos in set([(self.coords.x + sign(self.vel.x), self.coords.y), (self.coords.x, self.coords.y + sign(self.vel.y))]):
            if pos in self.blocks:
                block = self.blocks[pos]
                if block.data["collision_box"] != "none":
                    if self.vel.x != 0:
                        if pygame.Rect(block.pos.x, block.pos.y, BLOCK_SIZE, BLOCK_SIZE).collidepoint(self.world_pos.x + self.vel.x * dt, self.world_pos.y):
                            self.vel.x = 0
                            break
                    if self.vel.y != 0:
                        if pygame.Rect(block.pos.x, block.pos.y, BLOCK_SIZE, BLOCK_SIZE).collidepoint(self.world_pos.x, self.world_pos.y + self.vel.y * dt):
                            self.vel.y = 0
                            break

        super().update(dt, **kwargs)

    def move(self, dt: float) -> None:
        # Fall
        self.vel.y += pps(GRAVITY) * dt
        # X-velocity gets decreased over time
        self.vel.x *= 0.93

class EnvironmentalParticle(Particle):
    """A superclass for particles that act as enviromental (add atmosphere)"""

    def __init__(self, pos: tuple, vel: tuple, survive_time: float, image: Surface, blocks: dict, layer: LayersEnum = LayersEnum.ENV_PARTICLES, master=None) -> None:
        super().__init__(pos, vel, survive_time, image, layer, master)
        self.blocks = blocks
        self.vel = pps(VEC(vel))

    def update(self, dt: float, **kwargs) -> None:
        super().update(dt, **kwargs)

        # If the particle floats behind a block, there is no point to continue rendering it
        if inttup(self.coords) in self.blocks:
            self.kill()
            return

        # Same goes when the particle floats outside the screen
        if not (0 < self.pos[0] < WIDTH and 0 < self.pos[1] < HEIGHT):
            self.kill()

class BlockParticle(PhysicsParticle):
    def __init__(self, pos: tuple[int, int], blocks: dict[tuple[int, int], Block], master: Block, layer: LayersEnum = LayersEnum.REG_PARTICLES) -> None:
        self.master = master
        self.pos = pos
        self.size = randint(6, 8)

        # Gets a random colour from master and fills its image with it
        self.image = pygame.Surface((self.size, self.size))
        color = self.master.image.get_at((randint(0, MIN_BLOCK_SIZE-1), randint(0, MIN_BLOCK_SIZE-1)))
        self.image.fill(color)

        # Calculate the time that the particle is going to last for
        self.survive_time = randint(4, 8) / 10
        super().__init__(self.pos, (randint(-35, 35) / 10, randint(-30, 5) / 10), self.survive_time, self.image, blocks, layer, master=master)

        # If the color is white which is the default blank color, it means that it is a transparent pixel, so don't generate
        if color == (255, 255, 255):
            self.kill()

    @staticmethod
    def spawn(pos: tuple[int, int], blocks: dict[tuple[int, int], Block]):
        for _ in range(randint(18, 26)):
            BlockParticle(VEC(pos) * BLOCK_SIZE + VEC(randint(0, BLOCK_SIZE), randint(0, BLOCK_SIZE)), blocks, blocks[pos])

class PlayerFallParticle(BlockParticle):
    """End class that handles the particles created when falling 4 blocks or more"""

    def __init__(self, pos: tuple[int, int], blocks: dict[tuple[int, int], Block], master: Block) -> None:
        super().__init__(pos, blocks, master)
        self.vel = VEC(randint(-60, 60) / 10, randint(-70, -20) / 10)

    @staticmethod
    def spawn(pos: tuple[int, int], blocks: dict[tuple[int, int], Block], master: Block, amount: tuple[int, int], layer: LayersEnum = LayersEnum.REG_PARTICLES):
        for _ in range(randint(*amount)):
            __class__(VEC(pos) * BLOCK_SIZE + VEC(randint(0, BLOCK_SIZE), BLOCK_SIZE-1), blocks, master)

class VoidFogParticle(GradualSpawningParticle, EnvironmentalParticle):
    """Class that handles the void fog particles thats spawn at the bottom of the world"""

    max_speed = 12
    max_spawn_frequency = 0.0027
    timer = time.time()

    def __init__(self, pos: tuple[int, int], size: tuple[int, int], blocks: dict[tuple[int, int], Block]) -> None:
        self.vel = randint(-(ms := __class__.max_speed), ms) / 10, randint(-ms, ms) / 10
        self.size = size
        self.image = pygame.Surface((self.size, self.size))
        self.color = Color((randint(15, 40), ) * 3)
        self.survive_time = randint(5, 12) / 10
        self.image.fill(self.color)
        self.pos = pos
        super().__init__(self.pos, self.vel, self.survive_time, self.image, blocks)

    @classmethod
    def spawn(cls, cam_pos: VEC, blocks: dict[tuple[int, int], Block], player_y: int):
        spawn_frequency = __class__.max_spawn_frequency + (player_y_perc := (MAX_Y - player_y) / (MAX_Y / 8)) * 0.02
        size = choices(range(5, 10+1), weights=[i ** (3 * player_y_perc) for i in range(12, 0, -2)])[0]
        super().spawn(player_y >= MAX_Y * 7 / 8, spawn_frequency, VEC(randint(0, WIDTH), randint(0, HEIGHT)) + cam_pos, size, blocks)