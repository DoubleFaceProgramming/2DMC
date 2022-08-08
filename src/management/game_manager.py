# 2DMC is a passion project to recreate the game "Minecraft" (all credit to Mojang Studios) in 2D.
# Copyright (C) 2022 Doubleface
# You can view the terms of the GPL License in LICENSE.md

# The majority of the game assets are properties of Mojang Studios,
# you can view their TOS here: https://account.mojang.com/documents/minecraft_eula

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.management.scenes import Scene

import pygame
import sys

from pygame.locals import DOUBLEBUF, HWSURFACE, QUIT, K_F3, KEYDOWN
from enum import Enum

from src.utils.constants import WIDTH, HEIGHT, SCR_DIM
from src.management.game import Game

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
            self.draw()

        self.kill()

    def update(self):
        self.dt = self.clock.tick_busy_loop() / 1000
        pygame.display.set_caption(f"2DMC | {self.clock.get_fps():.2f}")
        self.events = {event.type: event for event in pygame.event.get()}

        if QUIT in self.events:
            self.kill()

        if KEYDOWN in self.events:
            if self.events[KEYDOWN].key == K_F3:
                self.debug = not self.debug

        self.scene.update()

    def draw(self):
        self.scene.draw()
        pygame.display.flip()

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
        # JIC, this is for if a scene needs to be saved and swapped back
        # (ex. pause menu, when exited will resume the saved scene of the game)
        self.scene.kill()
        self.scene = scene
        self.scene.start()