from random import randint, seed, choices
from pygame.draw import rect as drawrect
from opensimplex import OpenSimplex
from pygame import Rect, Surface
from functools import cache
from os.path import join
from pathlib import Path
from vnoise import Noise
from os import listdir
from math import ceil
import numpy as np

from src.constants import CHUNK_SIZE, BLOCK_SIZE, ORE_DISTRIBUTION, SEED, WIDTH, HEIGHT, CONFLICTING_STRUCTURES, MAX_Y, STRUCTURES, BLOCK_DATA
from src.utils import ascii_str_sum, canter_pairing, rand_bool
from src.block import Block
from src.player import Camera
from build.exe_comp import pathof

seed(SEED)
snoise = OpenSimplex(seed=SEED)
pnoise = Noise(SEED)

class Structure(object):
    instances = {}

    def __init__(self, name: str, block_data: dict):
        self.name = name
        self.block_data = block_data
        self.in_chunks = set([(block_pos[0] // CHUNK_SIZE, block_pos[1] // CHUNK_SIZE) for block_pos in block_data])
        self.blocks_in_chunk = {}
        for chunk in self.in_chunks:
            if chunk in self.__class__.instances:
                self.__class__.instances[chunk].append(self)
            else:
                self.__class__.instances[chunk] = [self]
            self.blocks_in_chunk[chunk] = {}
        for block_pos, block_name in self.block_data.items():
            chunk = (block_pos[0] // CHUNK_SIZE, block_pos[1] // CHUNK_SIZE)
            self.blocks_in_chunk[chunk][block_pos] = block_name

class StructureGenerator(object):
    """Class that handles the generation of structures"""
    def __init__(self, name, obstruction=False):
        self.name = name
        self.on_surface = True
        self.obstruction = obstruction
        self.files = STRUCTURES[name]
        self.distribution = STRUCTURES[name]["distribution"]
        self.BLOCK_DATA = {}

        self.get_max_size()
        self.get_max_chunks()

    def get_max_size(self) -> None:
        """Get the maximum dimensions of all the possible variations of this structure"""
        max_sizes = []
        for file in self.files:
            if file != "distribution":
                self.BLOCK_DATA[file] = STRUCTURES[self.name][file]
                # Append the max size of all the different possible variations
                max_sizes.append((max(x for x, y in self.BLOCK_DATA[file][1]) - min(x for x, y in self.BLOCK_DATA[file][1]) + 1,
                                  max(y for x, y in self.BLOCK_DATA[file][1]) - min(y for x, y in self.BLOCK_DATA[file][1]) + 1))
        # Get the biggest one
        self.max_size = max(max_sizes)

    def get_max_chunks(self) -> None:
        """Get the maximum number of chunks the structure could span from the max_size"""
        for conflicts in CONFLICTING_STRUCTURES:
            if self.name in CONFLICTING_STRUCTURES[conflicts]:
                self.chunks_to_check = major_structure_generators[conflicts[0]].chunks_to_check
                break
        else:
            self.chunks_to_check = int(ceil((self.max_size[0] + 7) / CHUNK_SIZE)) + 1, int(ceil((self.max_size[1] + 7) / CHUNK_SIZE) + 1)

    def generate(self, origin: tuple, chunk_pos: tuple, chunk_data: dict) -> Structure | None:
        """Generates chunk data that includes a structure at the given origin

        Args:
            origin (tuple): The position of the block where the structure is going to start generating from
            chunk_pos (tuple): The original chunk position of the structure
            chunk_data (dict): The block data of the chunk the structure is originally in

        Returns:
            Structure | None: A Structure object with the resulting block data
        """

        seed(SEED + canter_pairing(origin) + ascii_str_sum(self.name)) # Seeding random-ness
        file = choices(self.distribution["files"], weights=self.distribution["weights"])[0] # Picking a random file using the files and weights generated in load_STRUCTURES()
        mirror = rand_bool(0.5) # Bool whether the structure should be flipped or not.
        block_data = {}

        for offset, block in self.BLOCK_DATA[file][1].items():
            if mirror: block_pos = (origin[0] + offset[0], origin[1] + offset[1]) # Mirror the structure if mirror is true
            else: block_pos = (origin[0] - offset[0], origin[1] + offset[1])
            if "," in block:  # If the block type is a random weighted choice between multiple blocks
                block_name = choices([i.split("=")[0] for i in block.split(",")],
                                     weights=[int(i.split("=")[1]) for i in block.split(",")])[0]
            else:
                block_name = block

            block_in_chunk = self.get_block_in_chunk(block_pos, chunk_pos, chunk_data)
            match self.can_generate(block_name, block_in_chunk):
                case 1:
                    block_data[block_pos] = block_name # Generate the block
                case 2:
                    return # Do not generate the entire structure
                case 3:
                    continue # Do not generate the block
                case 4:
                    block_data[block_pos] = BLOCK_DATA[block_name]["overwrite_and_change"][block_in_chunk]

        return Structure(self.name, block_data)

    def get_block_in_chunk(self, block_pos: tuple, chunk_pos: tuple, chunk_data: dict) -> str:
        # If the block is inside the chunk the structure originated from
        if 0 <= block_pos[0] - chunk_pos[0] * CHUNK_SIZE < CHUNK_SIZE and 0 <= block_pos[1] - chunk_pos[1] * CHUNK_SIZE < CHUNK_SIZE:
            if block_pos in chunk_data:
                block_in_chunk = chunk_data[block_pos] # Get the block name of the target position in the chunk
            else:
                block_in_chunk = "" # If the block does not exist in the chunk, set it to an empty string

        # real_chunk_pos is the actual chunk position of the current block, not the chunk the structure originates from
        if (real_chunk_pos := (block_pos[0] // CHUNK_SIZE, block_pos[1] // CHUNK_SIZE)) in Structure.instances:
            for structure in Structure.instances[real_chunk_pos]:       # Check for STRUCTURES that have already been pre-generated
                if block_pos in structure.block_data:                   # If the current block overlaps a block in the structure
                    block_in_chunk = structure.block_data[block_pos]    # Set the block in chunk to that block in the structure
                    break
            else:                                                       # If it did not find a structure that has been pre-generated
                if block_pos not in Chunk.generated_blocks:             # If the block have not been generated anywhere else
                    block_in_chunk = generate_block(*block_pos)         # Generate it
                    Chunk.generated_blocks[block_pos] = block_in_chunk  # Add the generated block to the list so that it
                else:                                                   # If the block has already been generated before
                    block_in_chunk = Chunk.generated_blocks[block_pos]  # Grab the block
        else:                                                           # If the structure in a chunk have not been generated
            if block_pos not in Chunk.generated_blocks:                 # Do what it did above and generate or grab the block
                block_in_chunk = generate_block(*block_pos)
                Chunk.generated_blocks[block_pos] = block_in_chunk
            else:
                block_in_chunk = Chunk.generated_blocks[block_pos]

        return block_in_chunk

    def can_generate(self, block_name: str, block_in_chunk: str) -> int:
        """

        Args:
            block_pos (tuple): the position of the block to generate
            block_name (str): the name of the block to generate
            chunk_pos (tuple): the position of the chunk that the structure originated from
            chunk_data (dict): the block data of the chunk that the structure originated from

        Returns:
            int: (
                1 means valid generation
                2 means invalid and the entire structure should not generate
                3 means invalid and only this specific block should not generate
                4 means valid but it would change to another block to replace the target block
            )
        """

        # Some tests to check if the block can replace the block it's generating on and if not, whether the entire structure can generate
        if block_in_chunk:
            # Overwriteable means which blocks the block can replace
            if "overwriteable" in BLOCK_DATA[block_name]:
                if block_in_chunk in BLOCK_DATA[block_name]["overwriteable"]:
                    return_value = 1
                elif self.obstruction:  # If obstruction is true it means that the entire structure should not generate if one block cannot generate
                    return_value = 2
                else:
                    return_value = 3
            # Can only overwrite is the same as overwriteable but it also cannot replace air
            elif "can_only_overwrite" in BLOCK_DATA[block_name]:
                if block_in_chunk in BLOCK_DATA[block_name]["can_only_overwrite"]:
                    return_value = 1
                elif self.obstruction:
                    return_value = 2
                else:
                    return_value = 3
            elif self.obstruction:
                return_value = 2
            else:
                return_value = 1
            if "overwrite_and_change" in BLOCK_DATA[block_name]:
                if block_in_chunk in BLOCK_DATA[block_name]["overwrite_and_change"]:
                    return_value = 4
        # If the block does not exist (air), and the block can't overwrite air
        elif "can_only_overwrite" in BLOCK_DATA[block_name]:
            return_value = 3
        else:
            return_value = 1

        return return_value

class BlobGenerator(StructureGenerator):
    def __init__(self, name, max_size, density, cycles, obstruction=False):
        self.name = name
        self.on_surface = False
        self.obstruction = obstruction
        self.max_size = max_size
        self.density = density
        self.cycles = cycles
        self.get_max_chunks()

    # Cache speeds up numpy array calculations
    @cache
    def CA(self, struct_seed: int, size: tuple, density: int, cycles: int) -> dict:
        """Function for generating a blob with the Cellular Automata algorithm

        Args:
            struct_seed (int): the unique seed for this blob, this chunk, this seed
            size (tuple): size of the grid in which to generate the blob
            density (int): how dense is the starting grid in the CA (Cellular Automata) algorithm
            cycles (int): how many CA (Cellular Automata) iterations to go through

        Returns:
            dict: A dict containing the block information of the blob
        """
        seed(struct_seed)

        is_empty = True
        while is_empty: # If after the algorithm the array is still empty, redo it
            blob = np.empty((size[1], size[0])) # Empty numpy array with specified dimensions

            # Populate density/11 of the array
            for y in range(size[1]):
                for x in range(size[0]):
                    blob[y, x] = not rand_bool(density / 11)

            neighbors_offset = [(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]

            for _ in range(cycles):                                   # Number of Cellular Automata iterations
                for y, line in enumerate(blob):                       # Go through each line
                    for x, block in enumerate(line):                  # Go through each block
                        neighbors = 0
                        for n in neighbors_offset:                    # Check every neighbor around the current block
                            try:                                      # Try and except for blocks around the edge of the list which lacks neighbors
                                if blob[y + n[0], x + n[1]]:              # If the neighboring block exists
                                    neighbors += 1                    # Increment the neighbor counter
                            except: pass
                        if neighbors <= 3:                            # If there are less than or equal to 3 neighboring blocks
                            blob[y, x] = False                        # That block disappears
                        elif neighbors > 5:                           # If there are more than 5 neighboring blocks
                            blob[y, x] = True                         # That block appears

            # Turn the list into a dictionary for structure generation
            blob_dict = {}
            for y, line in enumerate(blob):
                for x, block in enumerate(line):
                    if block:
                        is_empty = False
                        blob_dict[(x, y)] = self.name

        return blob_dict

    def generate(self, origin: tuple, chunk_pos: tuple, chunk_data: dict) -> Structure | None:
        """Generates chunk data that includes a structure at the given origin

        Args:
            origin (tuple): The position of the block where the structure is going to start generating from
            chunk_pos (tuple): The original chunk position of the structure
            chunk_data (dict): The block data of the chunk the structure is originally in

        Returns:
            Structure | None: A Structure object with the resulting block data
        """

        struct_seed = SEED + canter_pairing(origin) + ascii_str_sum(self.name)
        # Create a dictionary of the block data of the blob with Cellular Automata
        blob = self.CA(struct_seed, self.max_size, self.density, self.cycles)

        block_data = {}
        for offset, block in blob.items():
            # Convert the positions to real world position by adding the origin to the block position (offset)
            block_pos = (origin[0] + offset[0], origin[1] + offset[1])
            block_in_chunk = self.get_block_in_chunk(block_pos, chunk_pos, chunk_data)
            match self.can_generate(block, block_in_chunk):
                case 1:
                    block_data[block_pos] = block # Generate the block
                case 2:
                    return # Do not generate the entire structure
                case 3:
                    continue # Do not generate the block
                case 4:
                    block_data[block_pos] = BLOCK_DATA[block]["overwrite_and_change"][block_in_chunk]

        return Structure(self.name, block_data)

class Chunk(object):
    """The class responsible for updating and drawing chunks."""
    instances = {}
    generated_blocks = {}

    def __init__(self, pos: tuple) -> None:
        self.__class__.instances[pos] = self
        self.pos = pos
        self.block_data = self.generate(pos[0], pos[1])
        self.rect = Rect(0, 0, CHUNK_SIZE * BLOCK_SIZE, CHUNK_SIZE * BLOCK_SIZE)

    def update(self, camera: Camera) -> None:
        self.rect.topleft = (self.pos[0] * CHUNK_SIZE * BLOCK_SIZE - camera.pos[0],
                             self.pos[1] * CHUNK_SIZE * BLOCK_SIZE - camera.pos[1])

    def draw(self, camera: Camera, screen: Surface) -> None:
        # Calls the draw function for each of the blocks inside
        for block in self.block_data:
            if not block in Block.instances:
                Block.instances[block] = Block(self, block, self.block_data[block])
            Block.instances[block].draw(camera, screen)

    def debug(self, screen: Surface) -> None:
        drawrect(screen, (255, 255, 0), self.rect, width=1)

    def generate(self, x: int, y: int) -> dict:
        """Takes the chunk coordinates and returns a dictionary containing the block data inside the chunk"""

        chunk_data = {}
        for y_pos in range(CHUNK_SIZE):
            for x_pos in range(CHUNK_SIZE):
                block_pos = (x * CHUNK_SIZE + x_pos, y * CHUNK_SIZE + y_pos)

                # Generate each block
                if block_pos in self.__class__.generated_blocks:
                    block_name = self.__class__.generated_blocks[block_pos]
                else:
                    block_name = generate_block(block_pos[0], block_pos[1])
                    self.__class__.generated_blocks[block_pos] = block_name

                if block_name != "":
                    chunk_data[block_pos] = block_name

        # If the structure has already been pre-generated and saved in another chunk, don't generate it again
        if (x, y) in Structure.instances:
            for structure in Structure.instances[(x, y)]:
                for block_pos, block_name in structure.blocks_in_chunk[(x, y)].items():
                    chunk_data[block_pos] = block_name
        else:
            if -1 <= y <= 1: # Surface generations
                chunk_data = generate_structures(x, y, chunk_data, "oak_tree", 1, chance=33)
                chunk_data = generate_structures(x, y, chunk_data, "tall_grass", 4, chance=25)
            for ore, data in ORE_DISTRIBUTION.items():
                for section in data["sections"]:
                    if section["range"][0] <= y < section["range"][1]:
                        chunk_data = generate_structures(x, y, chunk_data, ore + "_ore", data["attempts_per_chunk"], dist=section)
                        break
            if MAX_Y // CHUNK_SIZE // 2 > y >= 0: # Everywhere underground above y-512
                chunk_data = generate_structures(x, y, chunk_data, "granite", 2, chance=14)
                chunk_data = generate_structures(x, y, chunk_data, "diorite", 2, chance=14)
                chunk_data = generate_structures(x, y, chunk_data, "andesite", 2, chance=14)
            elif MAX_Y // CHUNK_SIZE >= y >= MAX_Y // CHUNK_SIZE // 2:
                chunk_data = generate_structures(x, y, chunk_data, "tuff", 2, chance=20)

        return chunk_data

def get_structures(x: int, y: int, chunk_data: dict, generator: StructureGenerator, attempts: int, chance: int | None, dist: dict) -> list:
    """Get structures inside the current chunk (x, y)

    Args:
        x (int): chunk position x
        y (int): chunk position y
        chunk_data (dict): dictionary containing the block data of the current chunk
        generator (StructureGenerator): structure generator object to use to generate
        attempts (int): how many times it is going to attempt to generate per chunk
        chance (int or None): the chance of the structure generating per attempt
        dist (dict): the distribution dictionary containing: the range of the slope, the maximum rarity, and the direction of the slope

    Returns:
        list: a list containing the block data of each of the structures in the chunk
    """

    out = []
    seed(SEED + canter_pairing((x, y)) + ascii_str_sum(generator.name))
    if chance == None: # Has to be ""== None" because chance can also be 0
        upper = dist["range"][0]
        lower = dist["range"][1]
        slope = dist["slope"]
        rarity = dist["rarity"]
        chance = (((y - upper) if slope == 1 else (lower - y)) / (lower - upper) * rarity) if slope else rarity
    for _ in range(attempts):
        if rand_bool(chance / 100):
            start_x = x * CHUNK_SIZE + randint(0, CHUNK_SIZE)
            if generator.on_surface:
                # Generate on the surface of the world
                start_y = terrain_generate(start_x)[1] - 1
                # If it is cut off by a cave, don't generate
                if (92.7 < cave_generate((start_x / 70, start_y / 70)) < 103) or (92.7 < cave_generate((start_x / 70, (start_y + 1) / 70)) < 103):
                    return out
            else:
                start_y = y * CHUNK_SIZE + randint(0, CHUNK_SIZE)

            # Structures that are not in this chunk
            if not 0 <= start_y - y * CHUNK_SIZE < CHUNK_SIZE:
                return out

            structure = generator.generate((start_x, start_y), (x, y), chunk_data)
            if structure:
                if structure.block_data:
                    out.append(structure)

    return out

def generate_structures(x: int, y: int, chunk_data: dict, name: str, attempts: int, chance: int | None = None, dist: dict = {}) -> dict:
    """Check the surrounding chunks for structures that generates in the current chunk (x, y), and then returns the chunk data with the structure

    Args:
        x (int): chunk position x
        y (int): chunk position y
        chunk_data (dict): block data of the current chunk
        generator (StructureGenerator): the structure generator object to use to generate
        attempts (int): how many times it is going to attempt to generate per chunk
        chance (int or None, optional): the chance of the structure generating per attempt
        dist (dict, optional): the distribution dictionary containing: the range of the slope, the maximum rarity, and the direction of the slope

    Returns:
        dict: the chunk data with the structure
    """

    generator = structure_generators[name]
    # Check all chunks around the current chunk within the size limit of the structure
    for ox in range(-generator.chunks_to_check[0], generator.chunks_to_check[0] + 1):
        for oy in range(-generator.chunks_to_check[1], generator.chunks_to_check[1] + 1):
            # Get the surrounding STRUCTURES that might protrude into the current chunk
            structs = get_structures(x + ox, y + oy, chunk_data, generator, attempts, chance, dist)
            for struct in structs:
                for block, block_name in struct.block_data.items():
                    # If there are parts of that structure inside the current chunk, generate that part in this chunk
                    if 0 <= block[0] - x * CHUNK_SIZE < CHUNK_SIZE and 0 <= block[1] - y * CHUNK_SIZE < CHUNK_SIZE:
                        chunk_data[block] = block_name

    return chunk_data

# Since simplex noise here is generated with a function making use of numpy arrays, cache improves performance
@cache
def terrain_generate(x: int) -> tuple[float, float]:
    """Takes the x position of a block and returns the result of the simplex noise and also the height it has to generate at"""
    simplex_noise_height = snoise.noise2array(np.array([x * 0.1]), np.array([0]))
    return simplex_noise_height, -int(simplex_noise_height * 5) + 5

def cave_generate(coords: tuple) -> float:
    """Takes the coordinates of a block and returns the noise map value for cave generation"""
    noise_height = pnoise.noise2(coords[0], coords[1])
    noise_height = noise_height + 0.5 if noise_height > 0 else 0
    noise_height = int(pow(noise_height * 255, 0.9))
    return noise_height

def blended_blocks_generate(y: int, block: str, blend_y: int, block2: str = "") -> str:
    """Returns a block based on a 5 block blend of two blocks

    Args:
        y (int): The y of the block
        block (str): The first block to blend from
        blend_y (int): The y at where the blend should happen
        block2 (str, optional): The second block to blend to. Defaults to "".

    Returns:
        str: The name of the block that should be generated
    """

    block_name = ""
    if y >= blend_y - 5:   # If the block is within 5 blocks of the blend level:
        match blend_y - y: # Match on the block's level above the blend level
            case 1 | 2:    # If the block is 1 / 2 blocks above blend level, ect.
                block_name = choices([block, block2], [70, 30])[0]
            case 3:
                block_name = choices([block, block2], [50, 50])[0]
            case 4:
                block_name = choices([block, block2], [30, 70])[0]
            case _:              # If the block is within 5 blocks of the blend level but not one
                if y >= blend_y: # of the above it will be either layer 5 or below
                    block_name = block

    return block_name

def generate_block(x: int, y: int) -> str:
    """Gets the name of the block that would generate (apart from structures) at the given location"""

    seed(SEED + canter_pairing((x, y)))
    block_name = ""

    # Generating bedrock
    block_name = blended_blocks_generate(y, "bedrock", MAX_Y)

    # If the block has been chosen (ie. is bedrock) return, else generate it
    if block_name:
        return block_name

    # Generate the layer of blended deepslate underneath stone
    block_name = blended_blocks_generate(y, "deepslate", MAX_Y // 2, block2="stone")

    # Cave noise map
    cave_noise_map_coords = (x / 70, y / 70)
    # Don't generate blocks if it satifies a certain range of values in the cave noise map, AKA a cave
    cave_noise_map_value = cave_generate(cave_noise_map_coords)

    if not (92.7 < cave_noise_map_value < 103):
        # Height of the terrain
        height = terrain_generate(x)
        # The lowest height of dirt
        dirt_height = -int(height[0] * 3.2) + 10
        if y == height[1]:
            block_name = "grass_block"
        elif height[1] + 1 <= y < dirt_height:
            block_name = "dirt"
        elif MAX_Y // 2 - 4 > y >= dirt_height:
            block_name = "stone"
        elif y >= MAX_Y // 2:
            block_name = "deepslate"
        if y == height[1] - 1:
            if not (92.7 < cave_generate((x / 70, (y + 1) / 70)) < 103):
                if rand_bool(1 / 3):
                    block_name = "grass"
                if rand_bool(1 / 21):
                    block_name = choices(["poppy", "dandelion"], weights=[1, 2])[0]
    else:
        block_name = ""

    return block_name

def load_chunks(camera: Camera) -> list:
    """Generate, unload and delete chunks.

    Args:
        camera (Camera): The camera used to calculate which chunks should be rendered

    Returns:
        list: The list of rendered chunks.
    """

    rendered_chunks = []
    # Load the chunks that show up on the screen
    for y in range(HEIGHT // (CHUNK_SIZE * BLOCK_SIZE) + 2):
        for x in range(WIDTH // (CHUNK_SIZE * BLOCK_SIZE) + 2):
            chunk = (
                x - 1 + int(round(camera.pos.x / (CHUNK_SIZE * BLOCK_SIZE))),
                y - 1 + int(round(camera.pos.y / (CHUNK_SIZE * BLOCK_SIZE)))
            )
            rendered_chunks.append(chunk)
            # If the chunk has not yet been generated, create the chunk object
            if chunk not in Chunk.instances:
                Chunk.instances[chunk] = Chunk(chunk)

    unrendered_chunks = []
    # Check a bigger area around the camera to see if there are chunks that are still active but shouldn't be
    for y in range(HEIGHT // (CHUNK_SIZE * BLOCK_SIZE) + 4):
        for x in range(WIDTH // (CHUNK_SIZE * BLOCK_SIZE) + 4):
            chunk = (
                x - 2 + int(round(camera.pos.x / (CHUNK_SIZE * BLOCK_SIZE))),
                y - 2 + int(round(camera.pos.y / (CHUNK_SIZE * BLOCK_SIZE)))
            )
            # Add that chunk to "unrendered_chunks" if it is still being rendered
            if chunk in Chunk.instances:
                if chunk not in rendered_chunks:
                    unrendered_chunks.append(chunk)

    # Unrender all the chunks in "unrendered_chunks"
    for chunk in unrendered_chunks:
        for block in Chunk.instances[chunk].block_data:
            if block in Block.instances:
                Block.instances[block].kill()
                del Block.instances[block]

    return rendered_chunks

# Major structure means structures that have bigger chunk spans than the rest of its conflicting STRUCTURES
major_structure_generators = {
    "oak_tree": StructureGenerator("oak_tree"),
    "granite": BlobGenerator("granite", (10, 10), 5, 3, obstruction=True),
    "diorite": BlobGenerator("diorite", (10, 10), 5, 3, obstruction=True),
    "andesite": BlobGenerator("andesite", (10, 10), 5, 3, obstruction=True),
    "tuff": BlobGenerator("tuff", (10, 10), 5, 3, obstruction=True)
}
# Minor structures means structure that have smaller chunk spans therefore needs to increase it's chunk span to match the major STRUCTURES
minor_structure_generators = {
    "tall_grass": StructureGenerator("tall_grass", obstruction=True),
    "coal_ore": BlobGenerator("coal_ore", (8, 4), 4, 2),
    "iron_ore": BlobGenerator("iron_ore", (3, 4), 4, 1),
    "gold_ore": BlobGenerator("gold_ore", (3, 3), 4, 1),
    "lapis_ore": BlobGenerator("lapis_ore", (3, 3), 4, 1),
    "redstone_ore": BlobGenerator("redstone_ore", (3, 3), 4, 1),
    "diamond_ore": BlobGenerator("diamond_ore", (3, 3), 4, 1),
    "emerald_ore": BlobGenerator("emerald_ore", (2, 2), 1, 1),
    "deepslate_coal_ore": BlobGenerator("deepslate_coal_ore", (8, 4), 4, 2),
    "deepslate_iron_ore": BlobGenerator("deepslate_iron_ore", (3, 4), 4, 1),
    "deepslate_gold_ore": BlobGenerator("deepslate_gold_ore", (3, 3), 4, 1),
    "deepslate_lapis_ore": BlobGenerator("deepslate_lapis_ore", (3, 3), 4, 1),
    "deepslate_redstone_ore": BlobGenerator("deepslate_redstone_ore", (3, 3), 4, 1),
    "deepslate_diamond_ore": BlobGenerator("deepslate_diamond_ore", (3, 3), 4, 1),
    "deepslate_emerald_ore": BlobGenerator("deepslate_emerald_ore", (2, 2), 1, 1),
}
structure_generators = {**major_structure_generators, **minor_structure_generators}