from pathlib import Path
import pygame
import json
import os

from src.images import block_textures
from src.utils import pathof, inttup
from src.particle import Particle
from src.constants import *

# Load json block data into a dictionary
BLOCK_DATA = {}
for file in os.listdir(pathof("data/blocks/")):
    BLOCK_DATA[Path(file).stem] = json.loads(open(os.path.join(pathof("data/blocks/"), file), "r").read())

class Block(pygame.sprite.Sprite):
    """Class that handles the managaing, updating and drawing of blocks."""
    instances = {}

    def __init__(self, chunk, pos: tuple, name: str):
        pygame.sprite.Sprite.__init__(self)
        self.__class__.instances[tuple(pos)] = self
        self.name = name
        self.data = BLOCK_DATA[self.name]
        self.chunk = chunk
        self.coords = VEC(pos)
        self.pos = self.coords * BLOCK_SIZE
        self.neighbors = {
            "0 -1": inttup((self.coords.x, self.coords.y-1)),
            "0 1": inttup((self.coords.x, self.coords.y+1)),
            "-1 0": inttup((self.coords.x-1, self.coords.y)),
            "1 0": inttup((self.coords.x+1, self.coords.y))
        }
        self.image = block_textures[self.name]

        # Different hitbox types (currently only two)
        if self.data["collision_box"] == "full":
            self.rect = pygame.Rect(self.pos, (BLOCK_SIZE, BLOCK_SIZE))
        elif self.data["collision_box"] == "none":
            self.rect = pygame.Rect(self.pos, (0, 0))

    def update(self, chunks):
        # Check if the block is supported, if not then remove the block
        if not is_supported(self.pos, self.data, self.neighbors):
            remove_block(chunks, self.coords, self.data, self.neighbors)

    def draw(self, camera, screen):
        self.rect.topleft = self.pos - camera.pos
        screen.blit(self.image, self.rect.topleft)

def remove_block(chunks: dict, pos: tuple, data: dict, neighbors: dict) -> None:
    """Remove the block at the position given

    Args:
        chunks (dict): A dictionary containing all the chunks
        pos (tuple): The position which has a block to remove
        data (dict): Dictionary of block data
        neighbors (dict): The neighbours of the block to remove
    """

    pos = inttup(pos)
    # Create a random number of particles
    for _ in range(randint(18, 26)):
        Particle("block", VEC(pos) * BLOCK_SIZE + VEC(randint(0, BLOCK_SIZE), randint(0, BLOCK_SIZE)), master=Block.instances[pos])
    chunk = (pos[0] // CHUNK_SIZE, pos[1] // CHUNK_SIZE)
    # If the block is layered, instead of removing the block completely, change that block to the next layer
    if "next_layer" in data:
        Block.instances[pos] = Block(chunk, pos, data["next_layer"])
        chunks[chunk].block_data[pos] = data["next_layer"]
    else:
        # Remove the block from both the blocks dictionary AND the chunk information
        del Block.instances[pos]
        del chunks[chunk].block_data[pos]
    # After the block breaks, update its neighbors
    for neighbor in neighbors:
        if neighbors[neighbor] in Block.instances:
            Block.instances[neighbors[neighbor]].update(chunks)

def set_block(chunks: dict, pos: tuple, name: str, neighbors: dict) -> None:
    """Set the block at the position given to the block given

    Args:
        chunks (dict): Dictionary containing all the chunks
        pos (tuple): The position of the block to set
        name (str): The name of the block to set
        neighbors (dict): THe neighbours of the block
    """

    pos = inttup(pos)
    # Calculates the position of the chunk the block is in.
    chunk = (pos[0] // CHUNK_SIZE, pos[1] // CHUNK_SIZE)
    if chunk in chunks:
        # Create an entry in the block dictionary that contains a new Block object
        Block.instances[pos] = Block(chunks[chunk], pos, name)
        chunks[chunk].block_data[pos] = name
    for neighbor in neighbors:
        # Update the neighboring blocks
        if neighbors[neighbor] in Block.instances:
            Block.instances[neighbors[neighbor]].update(chunks)

def is_occupied(player, pos: tuple) -> bool:
    """Check if a block or the player overlaps with the position given

    Args:
        player (Player): The player
        pos (tuple): The position of the block that is being placed

    Returns:
        bool: Whether the given position is occupied or not
    """
    pos = inttup(pos)
    # Check if the player's rect is overlapping with the position of the block that is trying to be placed
    if not pygame.Rect(VEC(pos) * BLOCK_SIZE, (BLOCK_SIZE, BLOCK_SIZE)).colliderect(pygame.Rect(player.pos, player.size)):
        if pos in Block.instances: # If there is already a block there:
            # If the "replaceable" key is in the block's data, meaning that the block is directly replaceable (i.e. grass)
            return not "replaceable" in Block.instances[pos].data # This will return False if the block is replaceable and vice versa
        else:
            return False
    return True

def is_supported(pos: tuple, data: dict, neighbors: dict, second_block_pos: tuple=False) -> bool:
    """Checks if the given block data (data) of the block can be supported at the given position

    Args:
        pos (tuple): The position to check
        data (dict): The data information of the block
        neighbors (dict): The block's neighbours
        second_block_pos (tuple, optional): I don't know why this needs to exist but it does. Defaults to False.

    Returns:
        bool: Whether the block will be supported at the given position
    """

    if data["support"]:
        for support in (supports := data["support"]):
            if inttup(support.split(" ")) != inttup(VEC(second_block_pos)-VEC(pos)):
                # Check if each of the supporting blocks exist in the neighbors
                if neighbors[support] in Block.instances:
                    if Block.instances[neighbors[support]].name not in supports[support]:
                        return False
                else:
                    return False
            else:
                return True
    return True

def is_placeable(player, pos: tuple, data: dict, neighbors:dict, second_block_pos: tuple=False) -> bool:
    """Evaluates if a block is placeable at a given position

    Args:
        player (Player): The player
        pos (tuple): The position to check
        data (dict): The block data
        neighbors (dict): The block's neighbours
        second_block_pos (tuple, optional): Passed into is_supported for some unknown magical reason. Defaults to False.

    Returns:
        bool: If you can place the block or not
    """

    # Checking if the position occupied and supported.
    if not is_occupied(player, pos) and is_supported(pos, data, neighbors, second_block_pos=second_block_pos):
        return True
    return False