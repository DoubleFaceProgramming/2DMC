from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_manager import GameManager

from pyfastnoisesimd import Noise, NoiseType, FractalType, PerturbType
from pygame.locals import MOUSEBUTTONDOWN, K_LSHIFT
import pygame
import time

from my_profile import profile_chunk

from block import Location
from scenes import Scene
from chunk import Chunk
from constants import *

class Game(Scene):
    def __init__(self, manager: GameManager) -> None:
        super().__init__(manager)
        self.noise = Noise(SEED)
        self.noise.noiseType = NoiseType.PerlinFractal
        self.noise.frequency = 0.01
        self.noise.fractal.fractalType = FractalType.Billow
        self.noise.fractal.octaves = 3
        self.noise.fractal.lacunarity = 0.5
        self.noise.fractal.gain = 1
        self.noise.perturb.perturbType = PerturbType.Gradient
        self.noise.perturb.amp = 2
        self.noise.perturb.frequency = 0.2

    def setup(self) -> None:
        super().setup()

        start = time.time()
        avg = 0
        for x in range(WIDTH // CHUNK_PIXEL_SIZE):
            for y in range(HEIGHT // CHUNK_PIXEL_SIZE):
                one_chunk_start = time.time()
                Chunk(self.manager, (x, y))
                avg += time.time() - one_chunk_start
                avg /= 2
        print("TOTAL:", time.time() - start, "seconds")
        print("AVERAGE:", avg, "seconds")

    def update(self) -> None:
        keys = pygame.key.get_pressed()

        if MOUSEBUTTONDOWN in self.manager.events:
            mpos = VEC(pygame.mouse.get_pos())
            event = self.manager.events[MOUSEBUTTONDOWN]
            if event.button == 1:
                chunk_pos = mpos // CHUNK_PIXEL_SIZE
                if chunk_pos in Chunk.instances:
                    Chunk.instances[chunk_pos].kill()
                else:
                    if keys[K_LSHIFT]:
                        profile_chunk(Chunk, self.manager, chunk_pos)
                    else:
                        Chunk(self.manager, chunk_pos)
            elif event.button == 3:
                block_pos = mpos // BLOCK_SIZE
                if block_pos in Location.instances:
                    location = Location.instances[block_pos]
                    del location[location.get_highest()]

        super().update()

    def draw(self) -> None:
        self.manager.screen.fill(BG_COLOR)

        super().draw()