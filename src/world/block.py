# 2DMC is a passion project to recreate the game "Minecraft" (all credit to Mojang Studios) in 2D.
# Copyright (C) 2022 Doubleface
# You can view the terms of the GPL License in LICENSE.md

# The majority of the game assets are properties of Mojang Studios,
# you can view their TOS here: https://account.mojang.com/documents/minecraft_eula

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING: # Type annotations without causing circular imports
    from src.management.game_manager import GameManager


import pygame

from src.utils.constants import BLOCK_SIZE, WorldSlices
from src.utils.images import BLOCK_TEXTURES
import src.utils.hooks

class Block:
    def __init__(self, master: Location, name: str, worldslice: WorldSlices | int) -> None:
        self.master = master
        self.name = name
        self.data = {}
        self.image = BLOCK_TEXTURES[self.name]
        self.worldslice = WorldSlices(worldslice)

        if self.data["collision_box"] == "full":
            self.rect = pygame.Rect(self.pos, (BLOCK_SIZE, BLOCK_SIZE))
        elif self.data["collision_box"] == "none":
            self.rect = pygame.Rect(self.pos, (0, 0))

    def update(self):
        if not is_supported(self.pos, self.data, self.neighbors):
            remove_block(chunks, self.coords, self.data, self.neighbors)

class Location:
    instances: dict[tuple[int, int], Location] = {}

    def __init__(self, manager, coords: tuple[int, int]):
        self.coords = coords
        self.__class__.instances[self.coords] = self
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))

        self.blocks: list[Block | None, Block | None, Block | None] = [None, None, None]

    def __getitem__(self, key: WorldSlices | int):
        return self.blocks[WorldSlices(key)]

    def __setitem__(self, key: WorldSlices | int, value):
        self.blocks[WorldSlices(key)] = value
        self.update_image()

    def __delitem__(self, key: WorldSlices | int):
        self.blocks[WorldSlices(key)] = None
        self.update_image()

    def __contains__(self, key: WorldSlices | int):
        return bool(WorldSlices(key))

    def update_image(self):
        self.image.blits([(block, (0, 0)) for block in self.highest_opaque_block()])

    # TODO: use tag system for transparency
    def highest_opaque_block(self):
        rev = self.blocks.reverse_nip()
        for index, block in enumerate(rev):
            if not block: continue
            if block.name not in {"glass", "tall_grass", "tall_grass_top", "grass", "dandelion", "poppy"}: # <- tags go here
                return rev[:index + 1].reverse_nip()

        return self.blocks