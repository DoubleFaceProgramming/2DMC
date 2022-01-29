from random import randint, seed, choices, choice, randrange
from pygame.draw import rect as drawrect
from vnoise import Noise
from opensimplex import OpenSimplex
from pygame import Rect, Surface
from os.path import join
from pathlib import Path
from os import listdir
from math import ceil
import numpy as np
from functools import cache
import cProfile
import pstats

from src.constants import CHUNK_SIZE, BLOCK_SIZE, SEED, WIDTH, HEIGHT, CONFLICTING_STRUCTURES
from src.block import Block, BLOCK_DATA
from src.player import Camera
from src.utils import ascii_str_sum, canter_pairing, pathof

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
        self.files = structures[name]
        self.distribution = structures[name]["distribution"]
        self.BLOCK_DATA = {}

        self.get_max_size()
        self.get_max_chunks()

    def get_max_size(self) -> None:
        """Get the maximum dimensions of all the possible variations of this structure"""
        max_sizes = []
        for file in self.files:
            if file != "distribution":
                self.BLOCK_DATA[file] = structures[self.name][file]
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
            self.chunks_to_check = int(ceil((self.max_size[0] + 7) / CHUNK_SIZE)), int(ceil((self.max_size[1] + 7) / CHUNK_SIZE))

    def generate(self, origin: tuple, chunk_pos: tuple, chunk_data: dict) -> Structure | None:
        """Generates chunk data that includes a structure at the given origin
        Returns:
            dict: A dictionary containing the block data of the structure.
        """
        seed(SEED + canter_pairing(origin) + ascii_str_sum(self.name)) # Seeding random-ness
        file = choices(self.distribution["files"], weights=self.distribution["weights"])[0] # Picking a random file using the files and weights generated in load_structures()
        mirror = bool(randint(0, 1)) # Bool whether the structure should be flipped or not.
        block_data = {}

        for offset, block in self.BLOCK_DATA[file][1].items():
            if mirror: block_pos = (origin[0] + offset[0], origin[1] + offset[1])
            else: block_pos = (origin[0] - offset[0], origin[1] + offset[1])
            if "," in block:
                block_name = choices([i.split("=")[0] for i in block.split(",")],
                             weights=[int(i.split("=")[1]) for i in block.split(",")])[0]
            else:
                block_name = block

            match self.can_generate(block_pos, block_name, chunk_pos, chunk_data):
                case 1:
                    block_data[block_pos] = block_name # Generate the block
                case 2:
                    return # Do not generate the entire structure
                case 3:
                    continue # Do not generate the block

        return Structure(self.name, block_data)

    def can_generate(self, block_pos: tuple, block_name: str, chunk_pos: tuple, chunk_data: dict) -> int:
        if 0 <= block_pos[0]-chunk_pos[0]*CHUNK_SIZE < CHUNK_SIZE and 0 <= block_pos[1]-chunk_pos[1]*CHUNK_SIZE < CHUNK_SIZE:
            if block_pos in chunk_data:
                block_in_chunk = chunk_data[block_pos]
            else:
                block_in_chunk = ""

        if (real_chunk_pos := (block_pos[0] // CHUNK_SIZE, block_pos[1] // CHUNK_SIZE)) in Structure.instances:
            for structure in Structure.instances[real_chunk_pos]:
                if block_pos in structure.block_data:
                    block_in_chunk = structure.block_data[block_pos]
                    break
            else:
                if block_pos not in Chunk.generated_blocks:
                    block_in_chunk = generate_block(*block_pos)
                    Chunk.generated_blocks[block_pos] = block_in_chunk
                else:
                    block_in_chunk = Chunk.generated_blocks[block_pos]
        else:
            if block_pos not in Chunk.generated_blocks:
                block_in_chunk = generate_block(*block_pos)
                Chunk.generated_blocks[block_pos] = block_in_chunk
            else:
                block_in_chunk = Chunk.generated_blocks[block_pos]

        if block_in_chunk:
            if "overwriteable" in BLOCK_DATA[block_name]:
                if block_in_chunk in BLOCK_DATA[block_name]["overwriteable"]:
                    return_value = 1
                elif self.obstruction:
                    return_value = 2
                else:
                    return_value = 3
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

    @cache
    def CA(self, struct_seed: int, size: tuple, density: int, cycles: int) -> dict:
        """Function for generating a blob with the Cellular Automata algorithm

        Args:
            struct_seed (int): the unique seed for this blob, this chunk, this seed
            size (int): size of the grid in which to generate the blob
            density (int): how dense is the starting grid in the CA (Cellular Automata) algorithm
            cycles (int): how many CA (Cellular Automata) iterations to go through

        Returns:
            dict: A dict containing the block information of the blob
        """
        seed(struct_seed)

        is_empty = True
        while is_empty:
            blob = np.empty((size[1], size[0]))

            # Create a 2D list with density/11 filled with the block type (self.name)
            for y in range(size[1]):
                for x in range(size[0]):
                    blob[y, x] = not (randint(0, 10) < density)

            neighbors_offset = [(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]

            for _ in range(cycles):                                   # Number of Cellular Automata iterations
                for y, line in enumerate(blob):                       # Go through each line
                    for x, block in enumerate(line):                  # Go through each block
                        neighbors = 0
                        for n in neighbors_offset:                    # Check every neighbor around the current block
                            try:                                      # Try and except for blocks around the edge of the list which lacks neighbors
                                if blob[y+n[0],x+n[1]]:               # If the neighboring block exists (== self.name)
                                    neighbors += 1                    # Increment the neighbor counter
                            except: pass
                        if neighbors <= 3:                            # If there are less than or equal to 3 neighboring blocks
                            blob[y,x] = False                         # That block disappears
                        elif neighbors > 5:                           # If there are more than 5 neighboring blocks
                            blob[y,x] = True                          # That block appears

            # Turn the list into a dictionary for structure generation
            blob_dict = {}
            for y, line in enumerate(blob):
                for x, block in enumerate(line):
                    if block:
                        is_empty = False
                        blob_dict[(x, y)] = self.name

        return blob_dict

    def generate(self, origin: tuple, chunk_pos: tuple, chunk_data: dict) -> Structure | None:
        struct_seed = SEED + canter_pairing(origin) + ascii_str_sum(self.name)
        # Create a dictionary of the block data of the blob with Cellular Automata
        blob = self.CA(struct_seed, self.max_size, self.density, self.cycles)

        block_data = {}
        for offset, block in blob.items():
            # Convert the positions to real world position by adding the origin to the block position (offset)
            block_pos = (origin[0] + offset[0], origin[1] + offset[1])
            match self.can_generate(block_pos, block, chunk_pos, chunk_data):
                case 1:
                    block_data[block_pos] = block # Generate the block
                case 2:
                    return # Do not generate the entire structure
                case 3:
                    continue # Do not generate the block

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

        if (x, y) in Structure.instances:
            for structure in Structure.instances[(x, y)]:
                for block_pos, block_name in structure.blocks_in_chunk[(x, y)].items():
                    chunk_data[block_pos] = block_name
        else:
            if -1 <= y <= 1: # Surface generations
                chunk_data = generate_structures(x, y, chunk_data, "oak_tree", (1, 2))
                chunk_data = generate_structures(x, y, chunk_data, "tall_grass", (4, 3))
            if y >= 0: # Everywhere underground
                chunk_data = generate_structures(x, y, chunk_data, "coal_ore", (2, 15))
                chunk_data = generate_structures(x, y, chunk_data, "iron_ore", (2, 18))
            if y >= 5: # Lower than y-40
                chunk_data = generate_structures(x, y, chunk_data, "gold_ore", (1, 16))
            if y >= 7: # Lower than y-56
                chunk_data = generate_structures(x, y, chunk_data, "lapis_lazuli_ore", (1, 22))
            if y >= 10: # Lower than y-80
                chunk_data = generate_structures(x, y, chunk_data, "redstone_ore", (2, 14))
            if y >= 16: # Lower than y-128
                chunk_data = generate_structures(x, y, chunk_data, "diamond_ore", (1, 32))
            if y >= 20: # Lower than y-160
                chunk_data = generate_structures(x, y, chunk_data, "emerald_ore", (1, 32))
            if y >= 0: # Everywhere underground
                chunk_data = generate_structures(x, y, chunk_data, "granite", (2, 14))
                chunk_data = generate_structures(x, y, chunk_data, "diorite", (2, 14))
                chunk_data = generate_structures(x, y, chunk_data, "andesite", (2, 14))

        # print(time.time() - start)

        return chunk_data

def get_structures(x: int, y: int, chunk_data: tuple, generator: StructureGenerator, chance: tuple) -> list:
    """Get structures inside the current chunk (x, y)

    Args:
        x (int): chunk position x
        y (int): chunk position y
        generator (StructureGenerator): structure object to generate
        chance (tuple): the odds of the structure generating, (number-of-structure-possible-per-chunk, odds-off-the-structure-generating-per-block-in-chunk)

    Returns:
        list: a list containing the block data of the structures in the chunk
    """
    out = []
    seed(SEED + canter_pairing((x, y)) + ascii_str_sum(generator.name))
    for _ in range(chance[0]):
        if randint(0, chance[1]) == 0:
            start_x = x * CHUNK_SIZE + randrange(0, CHUNK_SIZE)
            if generator.on_surface:
                # Generate on the surface of the world
                start_y = terrain_generate(start_x)-1
                # If it is cut off by a cave, don't generate
                if (92.7 < cave_generate((start_x/70, start_y/70)) < 100) or (92.7 < cave_generate((start_x/70, (start_y+1)/70)) < 100):
                    return out
            else:
                start_y = y * CHUNK_SIZE + randrange(0, CHUNK_SIZE)

            # Structures that are not in this chunk
            if not 0 <= start_y - y * CHUNK_SIZE < CHUNK_SIZE:
                return out

            structure = generator.generate((start_x, start_y), (x, y), chunk_data)
            if structure:
                if structure.block_data:
                    out.append(structure)

    return out

def generate_structures(x: int, y: int, chunk_data: dict, name: str, chance: tuple) -> dict:
    """Check the surrounding chunks for structures that generates in the current chunk (x, y), and then returns the chunk data with the structure

    Args:
        x (int): chunk position x
        y (int): chunk position y
        chunk_data (dict): original chunk data
        generator (StructureGenerator): the structure object to generate
        chance (tuple): the odds of the structure generating, (number-of-structure-possible-per-chunk, odds-of-a-chunk-containing-the-structure)

    Returns:
        dict: the chunk data with the structure
    """
    generator = structure_generators[name]
    # Check all chunks around the current chunk within the size limit of the structure
    for ox in range(-generator.chunks_to_check[0], generator.chunks_to_check[0] + 1):
        for oy in range(-generator.chunks_to_check[1], generator.chunks_to_check[1] + 1):
            # Get the surrounding structures that might protrude into the current chunk
            structs = get_structures(x + ox, y + oy, chunk_data, generator, chance)
            for struct in structs:
                for block, block_name in struct.block_data.items():
                    # If there are parts of that structure inside the current chunk, generate that part in this chunk
                    if 0 <= block[0]-x*CHUNK_SIZE < CHUNK_SIZE and 0 <= block[1]-y*CHUNK_SIZE < CHUNK_SIZE:
                        chunk_data[block] = block_name

    return chunk_data

@cache
def terrain_generate(x: int) -> float:
    """Takes the x position of a block and returns the height it has to be at"""
    return -int(snoise.noise2array(np.array([x*0.1]), np.array([0]))*5)+5

def cave_generate(coords: tuple) -> float:
    """Takes the coordinates of a block and returns the noise map value for cave generation"""
    noise_height = pnoise.noise2(coords[0], coords[1])
    noise_height = noise_height + 0.5 if noise_height > 0 else 0
    noise_height = int(pow(noise_height * 255, 0.9))
    return noise_height

def generate_block(x, y):
    seed(canter_pairing((x, y)))
    # Cave noise map
    cave_noise_map_coords = (x/70, y/70)
    # Don't generate blocks if it satifies a certain range of values in the cave noise map, AKA a cave
    cave_noise_map_value = cave_generate(cave_noise_map_coords)

    block_name = ""
    if not (92.7 < cave_noise_map_value < 100):
        # Generate terrain
        height = terrain_generate(x)
        if y == height:
            block_name = "grass_block"
        elif height+1 <= y < height+4:
            block_name = "dirt"
        elif y >= height+4:
            block_name = "stone"
        if y == height-1:
            if not (92.7 < cave_generate((x/70, (y+1)/70)) < 100):
                if randint(0, 2) == 0:
                    block_name = "grass"
                if randint(0, 21) == 0:
                    block_name = choices(["poppy", "dandelion"], weights=[1, 2])[0]

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

def load_structures() -> dict:
    """Load the structure data files into a dictionary.

    Returns:
        dict: A dictionar containing structure information
    """

    # 104 lines of comments... maybe I went overboard xD
    # I hope I explained the file format well :)

    # reference structure file (short_oak_tree.structure)
    #
    # ---------------------------------------------------
    # 1:oak_log
    # 2:oak_leaves
    # 3:dirt
    # 4:leafed_oak_log
    # structure:
    #  222
    #  242
    # 22422
    # 22422
    #   1
    #   3
    # origin:
    # 2 4
    # ---------------------------------------------------

    # Folder references the folder containing the .structure and distribution files.
    # (Using pathof for exe compatibility)
    structures = dict()
    for folder in listdir(pathof("data/structures/")):
        structures[folder] = dict()
        for struct in listdir(join(pathof("data/structures/"), folder)): # Struct is a file in the aforementioned directory.
            if struct != "distribution.structure": # Any regular .structure file
                # A list containing each line of the .structure
                data = open(pathof(f"data/structures/{folder}/{struct}"), "r").readlines()

                split = data.index("structure:\n") # The line # of the end of the legend and beginning of the pattern
                split2 = data.index("origin:\n") # The line # of the end of the pattern and beginning of the origin

                legends = {legend.split(":")[0]: legend.split(":")[1] for legend in [legend[:-1] for legend in data[:split]]}
                # legend[:-1] is used to get rid of the newline character (\n or \r\n depending on the platform)
                # It results in:
                # ['1:oak_log', '2:oak_leaves', '3:dirt', '4:leafed_oak_log']
                # The left side of the colon is the number, the right side is the name
                # Resulting in: {
                #    1:"oak_log",
                #    2:"oak_leaves"
                # }, ect.

                structure = [line[:-1] for line in data[(split + 1):split2]]
                # data[(split + 1):split1] returns a list containing the pattern
                # ie.
                #  222
                #  242
                # 22422
                # ect.
                # Again, line[:-1] removes the newline character.

                origin = (int((origin_line := data[-1].split(' '))[0]), int(origin_line[1]))
                # data[-1] would be '2 4' in the example
                # Origin line is a *list* that would contain ["2", "4"] as *strings*
                # We turn that list into a tuple that contains integers.

                blocks = dict()
                for y in range(len(structure)):
                    for x in range(len(structure[y])):
                        # This loops through co-ordinates representing characters in the structures section
                        try:
                            # Checks if there is an entry in the legend for the number
                            # If x was 2 and y was 0, you could read this as:
                            # -> legends[structure[2][0]]
                            # -> legends[2] (If you look at the example and go 2 across and 0 down it would be 2)
                            # -> "oak_leaves"
                            # This value is not used, but it would throw a KeyError if there is no entry in the legend
                            # which would be passed and there would be no entry in the blocks list.
                            # However if there is an entry in the legend the else block will be run.
                            legends[structure[y][x]]

                        except: pass
                        else:
                            # Makes an entry in blocks.
                            # The key is the position of the block subtracted from the origin and
                            # the value is the entry in the legend at the current co-ordinates.
                            # ex. with the x = 2 and y = 0 example above
                            # blocks[(0, -4)] = "oak_leaves"
                            blocks[(x - origin[0], y - origin[1])] = legends[structure[y][x]]

                # Path(struct).stem gets the stem of the file (short_oak_tree.structure -> shoroak_tree)
                # This might be:
                # structures["oak_tree"][short_oak_tree] = ((2, 4), {
                #     (0, 4): "oak_leaves",
                #     ect.
                # })
                structures[folder][Path(struct).stem] = (origin, blocks)

            else: # This block of code handles distribution.structure specifically
                # Example distribution.structure
                # ---------------------
                # regular_oak_tree 57%
                # medium_oak_tree 18%
                # short_oak_tree 10%
                # large_oak_tree 8%
                # balloon_oak_tree 7%
                # ---------------------

                # A list containing each line of distribution.structure
                distribution = open(pathof(f"data/structures/{folder}/distribution.structure"), "r").readlines()

                # This can be read as:
                # For every line in the distribution, remove the last 2 characters,
                # split it on ' ' and turn the second element of the returned list into an integer.
                # Then adds this integer to a list.
                # Removing the last 2 characters removes the new line character and the percent symbol.
                # Splitting on ' ' might give ["regular_oak_tree", "57"], so an integer of the second element
                # would be 57.
                # The resulting list would be [57, 18, 10, 8, 7]
                weights = [int(line[:-2].split(' ')[1]) for line in distribution]

                # This does essentially the same thing as the previous comprehension,
                # it loops through each line and splits on ' ', but this time we take
                # the first element: ex. "regualar_oak_tree".
                # The resulting list would be:
                # [regular_oak_tree, medium_oak_tree, short_oak_tree, large_oak_tree, balloon_oak_tree]
                files = [line[:-2].split(' ')[0] for line in distribution]

                # We then add this to the structures dictionary. ex.
                # structures[oak_tree][distribution] = {
                #    "weights": [57, 18, 10, 8, 7],
                #    "files": [regular_oak_tree, medium_oak_tree, short_oak_tree, large_oak_tree, balloon_oak_tree],
                # }
                structures[folder]["distribution"] = {"weights": weights, "files": files}

    # We then return the final structures dictionary.
    return structures

structures = load_structures()

# Major structure means structures that have bigger chunk spans than the rest of its conflicting structures
major_structure_generators = {
    "oak_tree": StructureGenerator("oak_tree"),
    "granite": BlobGenerator("granite", (10, 10), 5, 3, obstruction=True),
    "diorite": BlobGenerator("diorite", (10, 10), 5, 3, obstruction=True),
    "andesite": BlobGenerator("andesite", (10, 10), 5, 3, obstruction=True)
}
# Minor structures means structure that have smaller chunk spans therefore needs to increase it's chunk span to match the major structures
minor_structure_generators = {
    "tall_grass": StructureGenerator("tall_grass", obstruction=True),
    "coal_ore": BlobGenerator("coal_ore", (8, 4), 4, 2),
    "iron_ore": BlobGenerator("iron_ore", (3, 4), 4, 1),
    "gold_ore": BlobGenerator("gold_ore", (3, 3), 4, 1),
    "lapis_lazuli_ore": BlobGenerator("lapis_lazuli_ore", (3, 3), 4, 1),
    "redstone_ore": BlobGenerator("redstone_ore", (3, 3), 4, 1),
    "diamond_ore": BlobGenerator("diamond_ore", (3, 3), 4, 1),
    "emerald_ore": BlobGenerator("emerald_ore", (2, 2), 1, 1)
}
structure_generators = {**major_structure_generators, **minor_structure_generators}