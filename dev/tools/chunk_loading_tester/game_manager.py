from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scenes import Scene

import pygame
import sys

from pygame.locals import DOUBLEBUF, HWSURFACE, QUIT, K_F3, KEYDOWN
from enum import Enum

from constants import *
from game import Game

class GameManager:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(SCR_DIM, DOUBLEBUF | HWSURFACE)
        self.clock = pygame.time.Clock()
        self.dt = self.clock.tick_busy_loop() / 1000
        self.debug = False

        self.scene = Game(self)
        self.scene.setup()

    def run(self):
        while self.scene.running:
            self.update()
            self.scene.draw()
            if self.debug:
                self.scene.debug()
            pygame.display.flip()

        self.kill()

    def update(self):
        self.dt = self.clock.tick_busy_loop() / 1000
        pygame.display.set_caption(f"Chunk Loading Tester {self.clock.get_fps():.0f}")
        self.events = {event.type: event for event in pygame.event.get()}

        if QUIT in self.events:
            self.kill()

        if KEYDOWN in self.events:
            if self.events[KEYDOWN].key == K_F3:
                self.debug = not self.debug

        self.scene.update()

    def kill(self) -> None:
        pygame.quit()
        sys.exit()

    # self.game.new_scene(self.game.Scenes.GAME)
    class Scenes(Enum):
        GAME = Game

    def new_scene(self, scene_class: Scene, **kwargs) -> None:
        self.scene.kill()
        self.scene = scene_class.value(self)
        self.scene.setup(**kwargs)

    def switch_scene(self, scene: Scene) -> None:
        self.scene.kill()
        self.scene = scene
        self.scene.start()