# 2DMC is a passion project to recreate the game "Minecraft" (all credit to Mojang Studios) in 2D.
# Copyright (C) 2022 Doubleface
# You can view the terms of the GPL License in LICENSE.md

# The majority of the game assets are properties of Mojang Studios,
# you can view their TOS here: https://account.mojang.com/documents/minecraft_eula

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.management.game_manager import GameManager

from pygame.locals import SRCALPHA
from random import seed, choice
import pygame

from src.utils.constants import VEC, CHUNK_SIZE, WIDTH, HEIGHT, CHUNK_PIXEL_SIZE, BLOCK_SIZE, SCR_DIM
from src.management.sprite import Sprite, LayersEnum
from src.utils.utils import pairing, PosDict
from src.world.block import Location

class ChunkData(PosDict):
    """Custom dictionary that also has methods that handle chunk generation"""
    def __init__(self, manager, master, chunk_pos):
        self.manager = manager
        self.master = master
        self.scene = self.manager.scene
        self.chunk_pos = VEC(chunk_pos)
        self.generate_base()

    def iterate(self):
        for y in range(int(self.chunk_pos.y * CHUNK_SIZE), int(self.chunk_pos.y * CHUNK_SIZE + CHUNK_SIZE)):
            for x in range(int(self.chunk_pos.x * CHUNK_SIZE), int(self.chunk_pos.x * CHUNK_SIZE + CHUNK_SIZE)):
                yield (x, y)

    def generate_base(self):
        seed(pairing(3, *self.chunk_pos, self.scene.seed))
        for pos in self.iterate():
            self[pos] = Location(self.manager, self.master, pos, *generate_location(pos))

class Chunk(Sprite):
    def __init__(self, manager: GameManager, chunk_pos: tuple[int, int] | VEC, chunk_data=None) -> None:
        super().__init__(manager, LayersEnum.BLOCKS)
        self.chunk_manager = self.scene.chunk_manager
        self.chunk_pos = VEC(chunk_pos)
        if not chunk_data:
            self.chunk_data = ChunkData(self.manager, self, self.chunk_pos)
        else:
            self.chunk_data = chunk_data
        self.image = pygame.Surface((CHUNK_PIXEL_SIZE, CHUNK_PIXEL_SIZE), SRCALPHA)
        for coords, location in self.chunk_data.items():
            self.update_image(VEC(coords), location.image)

    def update_image(self, coords, image):
        on_chunk_pos = VEC(coords.x % CHUNK_SIZE, coords.y % CHUNK_SIZE) * BLOCK_SIZE
        self.image.fill((0, 0, 0, 0), (*on_chunk_pos, BLOCK_SIZE, BLOCK_SIZE))
        self.image.blit(image, on_chunk_pos)

    def draw(self):
        self.manager.screen.blit(self.image, self.chunk_pos * CHUNK_PIXEL_SIZE - self.scene.player.camera.pos)
        pygame.draw.rect(self.manager.screen, (255, 255, 0), (*(self.chunk_pos * CHUNK_PIXEL_SIZE - self.scene.player.camera.pos), CHUNK_PIXEL_SIZE, CHUNK_PIXEL_SIZE), 2)

class ChunkManager:
    def __init__(self, manager):
        self.manager = manager
        self.scene = self.manager.scene
        self.chunks = PosDict()
        self.unloaded_chunk_data = PosDict()
        self.displayed_chunks = VEC(WIDTH // CHUNK_PIXEL_SIZE + 1, HEIGHT // CHUNK_PIXEL_SIZE + 1)
        self.topleft_chunk_pos = self.scene.player.chunk_coords - self.displayed_chunks // 2 - (1, 0)
        self.bottomright_chunk_pos = self.topleft_chunk_pos + self.displayed_chunks

    def update(self) -> None:
        self.topleft_chunk_pos = self.scene.player.camera.chunk_coords - self.displayed_chunks // 2 - (1, 0)
        self.bottomright_chunk_pos = self.topleft_chunk_pos + self.displayed_chunks
        new_chunks = PosDict()
        for y in range(int(self.topleft_chunk_pos.y), int(self.bottomright_chunk_pos.y + 1)):
            for x in range(int(self.topleft_chunk_pos.x), int(self.bottomright_chunk_pos.x + 1)):
                if (x, y) not in self.chunks: # If the chunk is inactive or ungenerated
                    # If it has been generated before and stored in old_chunk_data, use the chunk data from there
                    new_chunks[(x, y)] = Chunk(self.manager, (x, y), self.unloaded_chunk_data[(x, y)] if (x, y) in self.unloaded_chunk_data else None)
                else: # If the chunk is currently active
                    # It is in the new chunks, also in the current chunks, thus just copy the object over to new chunks
                    new_chunks[(x, y)] = self.chunks[(x, y)]
                    # Delete from current chunks, so that what's left can be stored in old_chunk_data below
                    del self.chunks[(x, y)]
        # Store the chunk data of the remaining chunks in old_chunk_data
        for chunk_pos, chunk in self.chunks.items():
            chunk.kill()
            self.unloaded_chunk_data[chunk_pos] = chunk.chunk_data
        self.chunks = new_chunks

def generate_location(coords):
    coords = VEC(coords)
    if coords.y == 0:
        name = "grass_block"
    elif 0 < coords.y <= 4:
        name = "dirt"
    elif coords.y > 4:
        name = choice(["stone", "andesite"])
    else:
        name = None
    return (name, name, name)