# 2DMC is a passion project to recreate the game "Minecraft" (all credit to Mojang Studios) in 2D.
# Copyright (C) 2022 Doubleface
# You can view the terms of the GPL License in LICENSE.md

# The majority of the game assets are properties of Mojang Studios,
# you can view their TOS here: https://account.mojang.com/documents/minecraft_eula

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.management.game_manager import GameManager

from src.management.sprite import Sprite, LayersEnum

# Location:
# (coords) -> Location -> Blocks
# Chunks:
# (chunk coords) -> Chunk -> Block data
# Block Data:
# (in-chunk coords) -> Reference to location (-> Blocks)
# Block:
# Block data - no references

# To update:
# Loop through every location, then through every block, then update the block
# Loop through every chunk, then generate a surface that contains every location's blitted texture
# -> Also generate a surface that contains every chunk if debug was activated (this surface would only have the debug information, not the block information. You would blit both textures)
# To Draw (or debug):
# Loop through every chunk and draw it
# -> If debug, draw normally, then draw the debug surf above it.

# Only chunks are sprites, and are the only ones called by the spritemanager.

class Chunk(Sprite):
    instances: dict[tuple[int, int], Chunk] = {}

    def __init__(self, manager: GameManager) -> None:
        super().__init__(manager, LayersEnum.BLOCKS)