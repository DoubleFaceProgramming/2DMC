# 2DMC is a passion project to recreate the game "Minecraft" (all credit to Mojang Studios) in 2D.
# Copyright (C) 2022 Doubleface
# You can view the terms of the GPL License in LICENSE.md

# The majority of the game assets are properties of Mojang Studios,
# you can view their TOS here: https://account.mojang.com/documents/minecraft_eula

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING: # Type annotations without causing circular imports
    from src.management.game_manager import GameManager
    from src.world.chunk import Chunk

from pygame.locals import SRCALPHA
import pygame

from src.utils.utils import PosDict, WorldSlices, SliceOverlay
from src.utils.constants import BLOCK_SIZE, VEC
from src.utils.images import BLOCK_TEXTURES
import src.utils.hooks

class Block:
    def __init__(self, master: Location, name: str, worldslice: WorldSlices | int) -> None:
        self.master = master
        self.name = name
        self.data = {}
        self.image = BLOCK_TEXTURES[self.name]
        self.worldslice = WorldSlices(worldslice)

        # if self.data["collision_box"] == "full":
        #     self.rect = pygame.Rect(self.pos, (BLOCK_SIZE, BLOCK_SIZE))
        # elif self.data["collision_box"] == "none":
        #     self.rect = pygame.Rect(self.pos, (0, 0))

    # def update(self): # TODO: Make sure this works :)
    #     if not is_supported(self.pos, self.data, self.neighbors):
    #         remove_block(chunks, self.coords, self.data, self.neighbors)

class Location:
    instances: dict[tuple[int, int], Location] = PosDict()

    def __init__(self, manager: GameManager, master: Chunk, coords: tuple[int, int], bg: None | Block = None, mg: None | Block = None, fg: None | Block = None):
        self.manager = manager
        self.master = master
        self.coords = VEC(coords)
        self.__class__.instances[self.coords] = self
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), SRCALPHA)

        self.blocks: list[Block | None, Block | None, Block | None] = [
            Block(self, bg, WorldSlices.BACKGROUND  ) if bg else None,
            Block(self, mg, WorldSlices.MIDDLEGROUND) if mg else None,
            Block(self, fg, WorldSlices.FOREGROUND  ) if fg else None
        ]
        self.update_image()

    def __getitem__(self, key: WorldSlices | int):
        return self.blocks[WorldSlices(key).value]

    def __setitem__(self, key: WorldSlices | int, value):
        self.blocks[WorldSlices(key).value] = value
        self.update_image()
        self.master.update_image(self.coords, self.image) # Cannot go in update_image() because locations are generated before chunks

    def __delitem__(self, key: WorldSlices | int):
        if key is not None:
            self.blocks[WorldSlices(key).value] = None
            self.update_image()
            self.master.update_image(self.coords, self.image) # Ditto

    def __contains__(self, key: WorldSlices | int):
        return self.blocks[WorldSlices(key).value] is None

    def update_image(self):
        self.image.fill((0, 0, 0, 0))
        for block in self.highest_opaque_block():
            if block:
                self.image.blit(block.image, (0, 0))
                self.image.blit(SliceOverlay[block.worldslice.name].value, (0, 0))

    def get_highest(self) -> None | WorldSlices:
        for block in self.blocks.reverse_nip():
            if block:
                return block.worldslice

    # TODO: use tag system for transparency
    def highest_opaque_block(self):
        """Get the blocks from the highest opaque block to the foreground"""
        rev = self.blocks.reverse_nip() # Reverse not in place - defined in hooks.py
        for index, block in enumerate(rev):
            if not block: continue
            if block.name not in {"glass", "tall_grass", "tall_grass_top", "grass", "dandelion", "poppy"}: # <- tags go here
                return rev[:index + 1].reverse_nip() # Return all blocks from the highest opaque block (index + 1) to the foreground

        return self.blocks # If the are no opaque blocks return self.blocks