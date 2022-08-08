# 2DMC is a passion project to recreate the game "Minecraft" (all credit to Mojang Studios) in 2D.
# Copyright (C) 2022 Doubleface
# You can view the terms of the GPL License in LICENSE.md

# The majority of the game assets are properties of Mojang Studios,
# you can view their TOS here: https://account.mojang.com/documents/minecraft_eula

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.management.game_manager import GameManager

from random import randint

from src.world.chunk import ChunkManager
from src.management.scenes import Scene
from src.entities.player import Player

class Game(Scene):
    def setup(self) -> None:
        super().setup()
        # Universal seed for profiling/timing: 50687767
        # Seeds for structure gen testing: -1797233725, -301804449, 1666679850, 1671665804
        # Seed for low world gen (loads at 1056) testing: 1561761502
        self.seed = randint(-2147483648, 2147483647)

        self.player = Player(self.manager)
        self.chunk_manager = ChunkManager(self.manager)

    def update(self):
        super().update()

        self.chunk_manager.update()