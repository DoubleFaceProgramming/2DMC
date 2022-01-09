import pygame
from pygame import Surface
import time

from src.constants import *
from src.utils import *

class Particle(pygame.sprite.Sprite):
    """Class that handles the management, updation and drawing of particles."""
    instances = []

    def __init__(self, type: str, pos: tuple, master=None) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.__class__.instances.append(self)
        self.type = type
        self.pos = VEC(pos)
        self.coords = self.pos // BLOCK_SIZE

        # Currently the only type of particle but more will be added
        if self.type == "block":
            self.size = randint(6, 8)
            self.image = pygame.Surface((self.size, self.size))
            self.vel = VEC(randint(-35, 35)/10, randint(-30, 5)/10)
            if master:
                self.master = master
                # Gets a random colour from master and fills its image with it
                color = self.master.image.get_at((randint(0, BLOCK_SIZE-1), randint(0, BLOCK_SIZE-1)))
                self.image.fill(color)
                if color == (255, 255, 255):
                    self.__class__.instances.remove(self)
                    self.kill()

        self.timer = time.time()
        self.survive_time = randint(4, 8) / 10

    def update(self, blocks: dict, dt: float) -> None:
        # If the particle's lifetime is greater than its intended lifetime, commit die
        if time.time() - self.timer > self.survive_time:
            self.__class__.instances.remove(self)
            self.kill()

        # Gravity
        if inttup(self.coords) in blocks:
            if blocks[inttup(self.coords)].data["collision_box"] == "none":
                self.vel.y += GRAVITY * dt
        else:
            self.vel.y += GRAVITY * dt

        self.vel.x *= 0.93

        neighbors = [
            inttup(self.coords),
            inttup((self.coords.x-1, self.coords.y)),
            inttup((self.coords.x+1, self.coords.y)),
            inttup((self.coords.x, self.coords.y-1)),
            inttup((self.coords.x, self.coords.y+1)),
        ]

        # Collision
        for pos in neighbors:
            if pos in blocks:
                block = blocks[pos]
                if block.data["collision_box"] != "none":
                    if pygame.Rect(block.pos.x, block.pos.y, BLOCK_SIZE, BLOCK_SIZE).collidepoint(self.pos.x + self.vel.x * dt, self.pos.y):
                        self.vel.x = 0
                        break
                    if pygame.Rect(block.pos.x, block.pos.y, BLOCK_SIZE, BLOCK_SIZE).collidepoint(self.pos.x, self.pos.y + self.vel.y * dt):
                        self.vel.y = 0
                        break

        self.pos += self.vel * dt
        self.coords = self.pos // BLOCK_SIZE

    def draw(self, camera, screen: Surface):
        screen.blit(self.image, (self.pos-camera.pos-VEC(self.image.get_size())/2))