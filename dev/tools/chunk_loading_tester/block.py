import pygame
import os

from utils import WorldSlices, PosDict, SliceOverlay
from constants import *
from utils import *
import hooks

pygame.init()
pygame.display.set_mode((0, 0))

# Loads each image in assets
block_images = {filename[:-4]: pygame.image.load(f"assets/{filename}").convert_alpha() for filename in os.listdir("assets")}

pygame.display.quit()

class Block:
    def __init__(self, master, name: str, worldslice: WorldSlices | int) -> None:
        self.master = master
        self.name = name
        self.data = {}
        self.image = block_images[self.name]
        self.worldslice = WorldSlices(worldslice)

class Location:
    instances = PosDict()

    def __init__(self, master, coords: tuple[int, int], bg: None | Block = None, mg: None | Block = None, fg: None | Block = None):
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

    def __getitem__(self, key: WorldSlices | int) -> None | Block:
        return self.blocks[WorldSlices(key).value]

    def __setitem__(self, key: WorldSlices | int, value) -> None:
        self.blocks[WorldSlices(key).value] = value
        self.update_image()
        self.master.update_image(self.coords, self.image)

    def __delitem__(self, key: WorldSlices | int) -> None:
        if key is not None:
            self.blocks[WorldSlices(key).value] = None
            self.update_image()
            self.master.update_image(self.coords, self.image)

    def __contains__(self, key: WorldSlices | int) -> bool:
        return self.blocks[WorldSlices(key).value] is None

    def update_image(self) -> None:
        """Updates its image to match the data"""
        self.image.fill((0, 0, 0, 0))
        for i, block in enumerate(self.highest_opaque_blocks()): # Gets all the visible blocks
            if not block: continue
            self.image.blit(block.image, (0, 0))
            # Blit each slice's corresponding transparent overlay
            self.image.blit(SliceOverlay[block.worldslice.name].value, (0, 0))

    def get_highest(self) -> None | WorldSlices:
        for block in self.blocks.reverse_3():
            if block:
                return block.worldslice.value

    # TODO: use tag system for transparency
    def highest_opaque_blocks(self):
        """Get the blocks from the highest opaque block to the foreground"""
        rev = self.blocks.reverse_3()
        for index, block in enumerate(rev):
            if not block: continue
            if block.name not in {"glass", "tall_grass", "tall_grass_top", "grass", "dandelion", "poppy"}: # <- tags go here
                return rev[:index + 1].reverse_3() # Return all blocks from the highest opaque block (index + 1) to the foreground

        return self.blocks # If the are no opaque blocks return self.blocks