# 2DMC is a passion project to recreate the game "Minecraft" (all credit to Mojang Studios) in 2D.
# Copyright (C) 2022 Doubleface
# You can view the terms of the GPL License in LICENSE.md

# The majority of the game assets are properties of Mojang Studios,
# you can view their TOS here: https://account.mojang.com/documents/minecraft_eula

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.management.scenes import Game

import pygame

from src.management.sprite import SpriteManager

class Scene:
    def __init__(self, manager: Game) -> None:
        self.manager = manager
        self.start()

    def setup(self) -> None:
        self.sprite_manager = SpriteManager(self.manager)

    def update(self) -> None:
        self.sprite_manager.update()

    def draw(self) -> None:
        self.sprite_manager.draw()

    def kill(self) -> None:
        self.running = False

    def start(self) -> None:
        self.running = True