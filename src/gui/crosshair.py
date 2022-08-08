# 2DMC is a passion project to recreate the game "Minecraft" (all credit to Mojang Studios) in 2D.
# Copyright (C) 2022 Doubleface
# You can view the terms of the GPL License in LICENSE.md

# The majority of the game assets are properties of Mojang Studios,
# you can view their TOS here: https://account.mojang.com/documents/minecraft_eula

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING: # Type annotations without causing circular imports
    from src.management.game_manager import GameManager
    from src.entities.player import Player

from src.management.sprite import Sprite, LayersEnum
from src.utils.constants import VEC

import pygame

class Crosshair(Sprite):
    """The class responsible for the drawing and updating of the crosshair"""

    def __init__(self, manager: GameManager, master: Player, changeover: int) -> None:
        super().__init__(LayersEnum.CROSSHAIR)

        self.master = master
        self.old_color = self.new_color = pygame.Color(0, 0, 0)
        self.changeover = changeover # Changeover defines the speed that the colour changes from old to new
        self.mpos = VEC(pygame.mouse.get_pos())
        self.block_pos = inttup((self.master.pos + (self.mpos - self.master.rect.topleft)) // BLOCK_SIZE)
        self.block = ""
        self.block_selection = self.BlockSelection(self, LayersEnum.BLOCK_SELECTION)
        self.grey = {*range(127 - 30, 127 + 30 + 1)} # A set that contains value from 97 to 157

    def update(self, dt: float, **kwargs) -> None:
        if self.new_color.r in self.grey and self.new_color.g in self.grey and self.new_color.b in self.grey:
            self.new_color = pygame.Color(255, 255, 255) # Checks if the colour is grey, and makes it white if it is

        self.new_color = pygame.Color(255, 255, 255) - self.new_color # Inverting the colour

        # Modified version of this SO answer, thank you!
        # https://stackoverflow.com/a/51979708/17303382
        self.old_color = [x + (((y - x) / self.changeover) * 100 * dt) for x, y in zip(self.old_color, self.new_color)]

        # Calculating the block beneath the mouse cursor
        self.mpos = VEC(pygame.mouse.get_pos())
        self.block_pos = inttup((self.master.pos + (self.mpos - self.master.rect.topleft)) // BLOCK_SIZE)
        if self.block_pos in Block.instances:
            self.block = Block.instances[inttup(self.block_pos)]
        else:
            self.block = ""

    def draw(self, screen: pygame.Surface, **kwargs) -> None:
        if not constants.MANAGER.cinematic.value["CH"] or self.master.inventory.visible: return
        self.new_color = self.get_avg_color(screen) # I know this is cursed it's the easiest way ;-;

        # The 2 boxes that make up the crosshair
        pygame.draw.rect(screen, self.old_color, (self.mpos[0] - 2, self.mpos[1] - 16, 4, 32))
        pygame.draw.rect(screen, self.old_color, (self.mpos[0] - 16, self.mpos[1] - 2, 32, 4))

    def debug(self, screen: Surface, **kwargs) -> None:
        if not self.master.inventory.visible:
            if self.block:
                # Displays the name of the block below the mouse cursor next to the mouse
                screen.blit(text(self.block.name.replace('_', ' ').title(), color=(255, 255, 255)), (self.mpos[0] + 12, self.mpos[1] - 36))

    def get_avg_color(self, screen: Surface) -> pygame.Color:
        """Gets the average colour of the screen at the crosshair using the position of the mouse and the game screen.
        Returns:
            pygame.Color: The average colour at the position of the crosshair
        """

        try:
            surf = screen.subsurface((self.mpos[0] - 16, self.mpos[1] - 16, 32, 32))
            color = pygame.Color(pygame.transform.average_color(surf))
        except:
            try: # This try / except fixes a mouse OOB crash at game startup
                color = screen.get_at(inttup(self.mpos))
            except:
                color = pygame.Color(255, 255, 255)

        return color

    class BlockSelection(Sprite):
        def __init__(self, crosshair, layer: LayersEnum = LayersEnum.BLOCK_SELECTION):
            super().__init__(layer)
            self.crosshair = crosshair

        def draw(self, screen: Surface, **kwargs):
            # Drawing a selection box around the block beneath the mouse (but 2px larger than the block)
            if not constants.MANAGER.cinematic.value["CH"] or self.crosshair.master.inventory.visible: return
            if self.crosshair.block:
                pygame.draw.rect(screen, (0, 0, 0), Rect((self.crosshair.block.rect.left - 2, self.crosshair.block.rect.top - 2, BLOCK_SIZE + 4, BLOCK_SIZE + 4)), 2)