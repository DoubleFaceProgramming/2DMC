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
import pygame

from src.utils.constants import SCR_DIM, BLOCK_SIZE, CHUNK_SIZE, VEC, DEBUG_SPACING
from src.utils.constants import BLUE_SKY
from src.world.chunk import ChunkManager
from src.management.scenes import Scene
from src.utils.utils import inttup, BPS
from src.entities.player import Player
from src.world.block import Location

FONT24 = pygame.font.Font("assets/fonts/regular.ttf", 24)
# so temporary you wouldnt even believe
def text(text: str, color: tuple=(0, 0, 0)):
    """Returns a surface which has the given text argument rendered using font 24 in the given colour (default black)"""
    return FONT24.render(text, True, color)

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
        
    def draw(self):
        self.manager.screen.fill(BLUE_SKY)
        
        super().draw()

    def debug(self) -> None:
        # Generating some debug values and storing in a dict for easy access.
        debug_values = {
            "FPS": int(self.manager.clock.get_fps()),
            "Seed": self.seed,
            "Velocity": (f"X: {round(BPS(self.player.vel.x), 4)} BPS, Y: {round(BPS(self.player.vel.y), 4)} BPS"),
            "Positon": inttup(self.player.coords),
            "Camera offset": inttup(self.player.pos - self.player.camera.pos - VEC(SCR_DIM) / 2 + self.player.size / 2),
            "Chunk": inttup(self.player.coords // CHUNK_SIZE),
            "Chunks loaded": len(self.chunk_manager.chunks),
            "Rendered blocks": len(Location.instances),
            "Block position": inttup((self.player.pos + (VEC(pygame.mouse.get_pos()) - self.player.rect.topleft)) // BLOCK_SIZE),
            # "Detecting rects": len(self.player.detecting_blocks),
            # "Particles": len(Particle.instances),
            # "Pre-gen cave heightmap": Chunk.cave_pregeneration_pos if Chunk.cave_pregeneration_bool else "Complete"
        }

        # Displaying the debug values.
        for line, name in enumerate(debug_values):
            self.manager.screen.blit(text(f"{name}: {debug_values[name]}"), (6, DEBUG_SPACING * line))
