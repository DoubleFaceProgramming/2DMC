from __future__ import annotations

from pygame import Color, Surface
from random import randint, choices
from typing import TYPE_CHECKING
import pygame
import time

from src.constants import VEC, BLOCK_SIZE, GRAVITY, WIDTH, HEIGHT, MAX_Y
from src.utils import inttup

if TYPE_CHECKING:
    from src.player import Camera
    from src.block import Block

class Particle():
    """A Common superclass for all particles"""
    instances = [] # List containing every particle, regardless of type

    def __init__(self, pos: tuple, vel: tuple, survive_time: float, image: Surface, master=None) -> None:
        self.__class__.instances.append(self)
        self.world_pos = VEC(pos)
        self.pos = self.world_pos
        self.vel = VEC(vel)
        self.coords = self.world_pos // BLOCK_SIZE
        self.survive_time = survive_time
        self.image = image
        # Set the time which the particle is going to last for
        self.start_time = time.time()
        self.master = master

    def update(self, dt: float, camera: Camera) -> None:
        # If the particle's lifetime is greater than its intended lifetime, commit die
        if time.time() - self.start_time > self.survive_time:
            self.kill()

        self.world_pos += self.vel * dt
        self.pos = self.world_pos - camera.pos
        self.coords = self.world_pos // BLOCK_SIZE

    def draw(self, screen: Surface, camera: Camera):
        screen.blit(self.image, (self.pos - VEC(self.image.get_size()) / 2))

    def kill(self) -> None:
        # There is a rare bug where the particle is killed twice,
        # therefore it is being removed from the list twice, so we catch that here
        try:
            self.__class__.instances.remove(self)
            del self
        except ValueError:
            pass

class PhysicsParticle(Particle):
    def __init__(self, pos: tuple, vel: tuple, survive_time: float, image: Surface, blocks: dict, master=None) -> None:
        self.blocks = blocks
        super().__init__(pos, vel, survive_time, image, master)

    def update(self, dt: float, camera: Camera) -> None:
        self.move(dt)

        neighbors = [
            inttup((self.coords.x-1, self.coords.y)),
            inttup((self.coords.x+1, self.coords.y)),
            inttup((self.coords.x, self.coords.y-1)),
            inttup((self.coords.x, self.coords.y+1)),
        ]

        # Collision with the blocks above, below, to the left and the right
        for pos in neighbors:
            if pos in self.blocks:
                block = self.blocks[pos]
                if block.data["collision_box"] != "none":
                    if pygame.Rect(block.pos.x, block.pos.y, BLOCK_SIZE, BLOCK_SIZE).collidepoint(self.world_pos.x + self.vel.x * dt, self.world_pos.y):
                        self.vel.x = 0
                        break
                    if pygame.Rect(block.pos.x, block.pos.y, BLOCK_SIZE, BLOCK_SIZE).collidepoint(self.world_pos.x, self.world_pos.y + self.vel.y * dt):
                        self.vel.y = 0
                        break

        super().update(dt, camera)

    def move(self, dt: float) -> None:
        # Fall
        self.vel.y += GRAVITY * dt
        # X-velocity gets decreased over time
        self.vel.x *= 0.93

class EnvironmentalParticle(Particle):
    def __init__(self, pos: tuple, vel: tuple, survive_time: float, image: Surface, blocks: dict, master=None) -> None:
        super().__init__(pos, vel, survive_time, image, master)
        self.blocks = blocks
        self.vel = VEC(vel)

    def update(self, dt: float, camera: Camera) -> None:
        super().update(dt, camera)
        
        # If the particle floats behind a block, there is no point to continue rendering it
        if inttup(self.coords) in self.blocks:
            self.kill()
            return
        
        # Same goes when the particle floats outside the screen
        if not (0 < self.pos[0] < WIDTH and 0 < self.pos[1] < HEIGHT):
            self.kill()

class BlockParticle(PhysicsParticle):
    def __init__(self, pos: tuple[int, int], blocks: dict[tuple[int, int], Block], master: Block) -> None:
        self.master = master
        self.pos = pos
        self.size = randint(6, 8)

        # Gets a random colour from master and fills its image with it
        self.image = pygame.Surface((self.size, self.size))
        color = self.master.image.get_at((randint(0, BLOCK_SIZE-1), randint(0, BLOCK_SIZE-1)))
        self.image.fill(color)

        # Calculate the time that the particle is going to last for
        self.survive_time = randint(4, 8) / 10
        super().__init__(self.pos, (randint(-35, 35) / 10, randint(-30, 5) / 10), self.survive_time, self.image, blocks, master=master)

        # If the color is white which is the default blank color, it means that it is a transparent pixel, so don't generate
        if color == (255, 255, 255):
            self.kill()

    @staticmethod
    def spawn(pos: tuple[int, int], blocks: dict[tuple[int, int], Block]):
        master = blocks[pos]
        for _ in range(randint(18, 26)):
            BlockParticle(VEC(pos) * BLOCK_SIZE + VEC(randint(0, BLOCK_SIZE), randint(0, BLOCK_SIZE)), blocks, master)
            
class PlayerFallParticle(BlockParticle):
    def __init__(self, pos: tuple[int, int], blocks: dict[tuple[int, int], Block], master: Block) -> None:
        super().__init__(pos, blocks, master)
        self.vel = VEC(randint(-60, 60) / 10, randint(-70, -20) / 10)
    
    @staticmethod
    def spawn(pos: tuple[int, int], blocks: dict[tuple[int, int], Block], master: Block, amount: tuple[int, int]):
        for _ in range(randint(*amount)):
            __class__(VEC(pos) * BLOCK_SIZE + VEC(randint(0, BLOCK_SIZE), BLOCK_SIZE-1), blocks, master)

class VoidFogParticle(EnvironmentalParticle):
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
        super().__init__(pos, self.vel, self.survive_time, self.image, blocks)

    @staticmethod
    def spawn(cam_pos: VEC, blocks: dict[tuple[int, int], Block], player_y: int):
        # If the player is below 7/8 of the world
        if player_y >= MAX_Y * 7 / 8:
            # The lower down the player is, the higher the frequency, the lower the frequency value, therefore more particles
            spawn_frequency = __class__.max_spawn_frequency + (player_y_perc := (MAX_Y - player_y) / (MAX_Y / 8)) * 0.02
            # If the time between last spawn and this call is more than frequency, spawn the particles
            if (elapsed_time := time.time() - __class__.timer) >= spawn_frequency:
                __class__.timer = time.time()
                # If the loop took longer than 1 * spawn_frequency, 
                # spawn multiple particles determined by elapsed_time / spawn_frequency
                for _ in range(round(elapsed_time / spawn_frequency)):
                    # It is exponentially more likely for large particles to spawn the lower down you are
                    size = choices(range(5, 10+1), weights=[i ** (3 * player_y_perc) for i in range(12, 0, -2)])[0]
                    __class__(VEC(randint(0, WIDTH), randint(0, HEIGHT)) + cam_pos, size, blocks)

# List of particles (superclasses) that should be drawn behind blocks
background_particles = (EnvironmentalParticle)