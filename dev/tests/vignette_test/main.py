import pygame
import sys

from vignette import *
from common import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | HWSURFACE)
clock = pygame.time.Clock()

class Block:
    instances = {}

    def __init__(self, pos: tuple[int, int], block: Blocks, worldslice: WorldSlice) -> None:
        self.__class__.instances[pos] = self
        self.coords = VEC(pos)
        self.pos = self.coords * BLOCK_SIZE
        self.block = block
        self.ws = worldslice

    def update(self) -> None:
        instances = self.__class__.instances
        self.neighbors = []
        for offset in NEIGHBORS:
            block_pos = inttup(self.coords + offset)
            if block_pos in instances and instances[block_pos].ws.value > self.ws.value:
                self.neighbors.append(inttup(offset))
        self.neighbors = tuple(self.neighbors)

    def draw(self) -> None:
        darken = SliceDarken[self.ws.name].value * (0.93 if not self.neighbors else 1)
        self.image = apply_vignette(self.block.name, self.neighbors, darken)
        screen.blit(self.image, self.pos)

    def kill(self) -> None:
        self.__class__.instances[inttup(self.coords)]

legend = {
    "1": (Blocks.dirt, WorldSlice.foreground),
    "2": (Blocks.dirt, WorldSlice.middleground),
    "3": (Blocks.dirt, WorldSlice.background),
    "4": (Blocks.grass_block, WorldSlice.foreground),
    "5": (Blocks.grass_block, WorldSlice.middleground),
}
blocks = [
    "1111111",
    "1212121",
    "1122211",
    "1223221",
    "2233322",
    "2233322",
    "1122211",
]

for y, row in enumerate(blocks):
    for x, ch in enumerate(row):
        if ch not in legend: continue
        Block((x, y), *legend[ch])

running = True
while running:
    clock.tick_busy_loop(FPS)
    pygame.display.set_caption(f"Vignette Test | {clock.get_fps():.0f}")

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == MOUSEBUTTONDOWN:
            m_pos = VEC(pygame.mouse.get_pos())
            block_pos = inttup(m_pos // BLOCK_SIZE)
            block = Block.instances[block_pos] if block_pos in Block.instances else None
            if event.button == 1:
                if block:
                    if block.ws.value != 1:
                        block.ws = WorldSlice(block.ws.value - 1)
                    else:
                        block.kill()
            elif event.button == 3:
                if block:
                    if block.ws.value != 3:
                        block.ws = WorldSlice(block.ws.value + 1)
                else:
                    Block(block_pos, "dirt")

    for block in Block.instances.values():
        block.update()

    screen.fill((135, 206, 250))
    for block in Block.instances.values():
        block.draw()

    pygame.display.flip()

pygame.quit()
sys.exit()