from pygame.math import Vector2 as VEC
import pygame

from pygame.locals import * # Dont do this normally! I'm only doing this for demonstration!

WIDTH, HEIGHT = SCR_DIM = (1200, 800)
SPEED = 500
FPS = 80

pygame.init()
screen = pygame.display.set_mode(SCR_DIM)
pygame.display.set_caption("Sprite System Demonstration")
clock = pygame.time.Clock()

class Player:
    def __init__(self, pos: VEC | tuple[int, int]) -> None:
        self.size = VEC(80, 80)
        self.pos = VEC(pos)
        self.vel = VEC(0, 0)

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        self.vel = VEC(0, 0)

        if keys[K_a]:
            self.vel.x -= SPEED
        if keys[K_d]:
            self.vel.x += SPEED
        if keys[K_w]:
            self.vel.y -= SPEED
        if keys[K_s]:
            self.vel.y += SPEED

        self.pos += self.vel * dt

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, (0, 0, 0), self.pos - (self.size / 2), self.size.x / 2)

class Square:
    instances = []

    def __init__(self, pos: tuple[int, int] | VEC, colour: tuple[int, int, int]):
        self.__class__.instances.append(self)

        self.size = VEC(100, 100)
        self.pos = VEC(pos)

        self.colour = colour

    def update(self) -> None:
        pass # While I could omit update() for this example, you rarely can in practise so I'll leave it here.

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.colour, pygame.Rect(*self.pos, *self.size))

player = Player((200, 200))

s_r = Square((400, 200), (255, 0, 0))
s_g = Square((400, 250), (0, 255, 0))
s_b = Square((400, 300), (0, 0, 255))

running = True
while running:
    screen.fill((255, 255, 255))
    dt = clock.tick_busy_loop(FPS) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for square in Square.instances:
        square.update()

    player.update(dt)

    for square in Square.instances:
        if square is not s_g:
            square.draw(screen)
    s_g.draw(screen)


    player.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()