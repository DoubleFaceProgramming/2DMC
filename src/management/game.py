# 2DMC is a passion project to recreate the game "Minecraft" (all credit to Mojang Studios) in 2D.
# Copyright (C) 2022 Doubleface
# You can view the terms of the GPL License in LICENSE.md

# The majority of the game assets are properties of Mojang Studios,
# you can view their TOS here: https://account.mojang.com/documents/minecraft_eula

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.management.game_manager import GameManager

from src.management.scenes import Scene

class Game(Scene):
    def __init__(self, game: GameManager) -> None:
        super().__init__(game)