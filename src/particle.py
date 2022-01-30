from pygame import Color, Surface
from random import randint
import pygame
import time

from src.constants import VEC, BLOCK_SIZE, GRAVITY
from src.utils import inttup

class Particle(pygame.sprite.Sprite):
    """Class that handles the management, updation and drawing of particles."""
    instances = []

    def __init__(self, pos: tuple, survive_time: float, image: Surface, master=None) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.__class__.instances.append(self)
        self.type = type
        self.pos = VEC(pos)
        self.vel = VEC(0, 0)
        self.coords = self.pos // BLOCK_SIZE
        self.survive_time = survive_time
        self.image = image
        # Set the time which the particle is going to last for
        self.start_time = time.time()
        self.master = master

    def update(self, dt: float) -> None:
        # If the particle's lifetime is greater than its intended lifetime, commit die
        if time.time() - self.start_time > self.survive_time:
            self.__class__.instances.remove(self)
            self.kill()

        self.pos += self.vel * dt
        self.coords = self.pos // BLOCK_SIZE

    def draw(self, camera, screen: Surface):
        screen.blit(self.image, (self.pos-camera.pos-VEC(self.image.get_size())/2))

class PhysicsParticle(Particle):
    def __init__(self, pos: tuple, survive_time: float, image: Surface, blocks: dict, master=None) -> None:
        self.blocks = blocks
        super().__init__(pos, survive_time, image, master)

    def update(self, dt: float) -> None:
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
                    if pygame.Rect(block.pos.x, block.pos.y, BLOCK_SIZE, BLOCK_SIZE).collidepoint(self.pos.x + self.vel.x * dt, self.pos.y):
                        self.vel.x = 0
                        break
                    if pygame.Rect(block.pos.x, block.pos.y, BLOCK_SIZE, BLOCK_SIZE).collidepoint(self.pos.x, self.pos.y + self.vel.y * dt):
                        self.vel.y = 0
                        break

        super().update(dt)

    def move(self, dt: float) -> None:
        # Fall
        self.vel.y += GRAVITY * dt
        # X-velocity gets decreased over time
        self.vel.x *= 0.93

class BlockParticle(PhysicsParticle):
    def __init__(self, pos: tuple, blocks: dict, master=None) -> None:
        self.master = master
        self.size = randint(6, 8)

        # Gets a random colour from master and fills its image with it
        self.image = pygame.Surface((self.size, self.size))
        color = self.master.image.get_at((randint(0, BLOCK_SIZE-1), randint(0, BLOCK_SIZE-1)))
        self.image.fill(color)

        self.survive_time = randint(4, 8) / 10
        super().__init__(pos, self.survive_time, self.image, blocks, master=master)
        self.vel = VEC(randint(-35, 35) / 10, randint(-30, 5) / 10)

        if color == (255, 255, 255):
            self.__class__.instances.remove(self)
            self.kill()

    def update(self, dt: float):
        super().update(dt)

class EnvironmentalParticle(Particle):
    def __init__(self, pos: tuple, survive_time: float, image: Surface, vel: tuple, master=None) -> None:
        super().__init__(pos, survive_time, image, master)
        self.vel = VEC(vel)

class VoidFogParticle(EnvironmentalParticle):
    max_speed = 30
    
    def __init__(self, pos: tuple) -> None:
        self.survive_time = randint(6, 10) / 10
        self.pos = pos
        self.size = randint(8, 12)
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(Color((randint(50, 100), ) * 3))
        self.vel = VEC(randint(-(ms := self.__class__.max_speed), ms) / 10, randint(-ms, ms) / 10)
        super().__init__(pos, self.survive_time, self.image, self.vel)