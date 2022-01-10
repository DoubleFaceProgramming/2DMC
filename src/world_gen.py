from random import randint, seed, choices, randrange
from pygame.draw import rect as drawrect
from perlin_noise import PerlinNoise
from opensimplex import OpenSimplex
from pygame import Rect, Surface
from os.path import join
from os import listdir
from math import ceil

from src.constants import CHUNK_SIZE, BLOCK_SIZE, SEED, WIDTH, HEIGHT
from src.block import Block, BLOCK_DATA
from src.utils import pathof

seed(SEED)
snoise = OpenSimplex(seed=SEED)
pnoise = PerlinNoise(seed=SEED)

class StructureGenerator(object):
    """Class that handles the generation of structures"""
    def __init__(self, folder, obstruction=False):
        self.folder = folder
        self.obstruction = obstruction
        self.files = structures[folder]
        self.distribution = structures[folder]["distribution"]
        self.BLOCK_DATA = {}

        # Get the maximum dimensions of all the possible variations of this structure
        max_sizes = []
        for file in self.files:
            if file != "distribution":
                self.BLOCK_DATA[file] = structures[folder][file]
                # Append the max size of all the different possible variations
                max_sizes.append((max(x for x, y in self.BLOCK_DATA[file][1]) - min(x for x, y in self.BLOCK_DATA[file][1]) + 1,
                            max(y for x, y in self.BLOCK_DATA[file][1]) - min(y for x, y in self.BLOCK_DATA[file][1]) + 1))
        # Get the biggest one
        self.max_size = max(max_sizes)

        # Get the maximum number of chunks the structure could span from the "max_size"
        self.chunks_to_check = int(ceil(self.max_size[0] / CHUNK_SIZE)), int(ceil(self.max_size[1] / CHUNK_SIZE))

    def generate(self, origin: tuple) -> dict:
        """Generates chunk data that includes a structure at the given origin

        Returns:
            dict: A dictionary containing the block data of the structure.
        """
        seed(SEED + origin[0] * CHUNK_SIZE + origin[1] * CHUNK_SIZE) # Seeding random-ness
        file = choices(self.distribution["files"], weights=self.distribution["weights"])[0] # Picking a random file using the files and weights generated in load_structures()
        mirror = bool(randint(0, 1)) # Bool whether the structure should be flipped or not.

        # Generating a dictionary containing block data for the structure.
        # self.BLOCK_DATA contains a key for each type of structure that can be generated by the StructureGenerator.
        # self.BLOCK_DATA["short_oak_tree"], for example, contains a tuple - the first element is the origin of the
        # structure (which is not used) and the second is the block data of the structure, which is a dict.
        # The key of this dict is the offset from origin, and the value is the block name.
        # The left hand side of the colon is the position of the block - if we should mirror the structure (flip it),
        # we add the x values of origin and offset for every item, otherwise we subtract it.
        # The right hand side of the colon contains the block name. However, sometimes there is a random choice between
        # 2 different blocks - for example: 'oak_leaves=50,leafed_oak_log=50'. This means that there is a 50% chance of
        # getting oak_leaves and a 50% chance of leafed_oak_log. However sometimes it is guaranteed that we get a specific
        # block - ex. 'oak_leaves'
        # We parse this by just using the value of block_name if it does not contain a comma, however if it does we use the
        # random.choices() function to decide which block to use. choices() takes to arguments, the options to choose from
        # and the arguments for each one: we get the choices by splitting the string by ',' (["oak_leaves=50", "leafed_oak_log=50"]),
        # then splitting each element in that list by '=' (["oak_leaves", "50"] and ["leafed_oak_log" "50"]) then getting the first
        # element of each of those, resulting in ["oak_leaves", "leafed_oak_log"]. To get the weights, we do the exact same process
        # but get the second element of (["oak_leaves", "50"] and ["leafed_oak_log" "50"]) and cast it into an integer, resulting
        # in [50, 50]. This process results in: choices(["oak_leaves", "leafed_oak_log"], weights=[50, 50]).

        # An example of the return data might be:
        # {
        #    (-30, -6): 'oak_leaves',
        #    ...
        #    (-30, -5): 'leafed_oak_log'
        #    ...
        #    (-30, 1): 'oak_log'
        #    ...
        #    (-30, 5): 'dirt'
        #    ect.
        # }

        # This is one beautiful piece of code isn't it?
        block_data = {
            (origin[0] + offset[0] if mirror else origin[0] - offset[0], origin[1] + offset[1]):
            (block if "," not in block else (choices([i.split("=")[0] for i in block.split(",")],
            weights=[int(i.split("=")[1]) for i in block.split(",")])[0]))
            for offset, block in self.BLOCK_DATA[file][1].items()
        }

        return block_data

class Chunk(object):
    """The class responsible for updating and drawing chunks."""
    instances = {}

    def __init__(self, pos: tuple) -> None:
        self.__class__.instances[pos] = self
        self.pos = pos
        self.block_data = self.generate(pos[0], pos[1])
        self.rect = Rect(0, 0, CHUNK_SIZE * BLOCK_SIZE, CHUNK_SIZE * BLOCK_SIZE)

    def update(self, camera) -> None:
        self.rect.topleft = (self.pos[0] * CHUNK_SIZE * BLOCK_SIZE - camera.pos[0],
                             self.pos[1] * CHUNK_SIZE * BLOCK_SIZE - camera.pos[1])

    def draw(self, camera, screen: Surface) -> None:
        # Calls the draw function for each of the blocks inside
        for block in self.block_data:
            if not block in Block.instances:
                Block.instances[block] = Block(self, block, self.block_data[block])
            Block.instances[block].draw(camera, screen)

    def debug(self, screen: Surface) -> None:
        drawrect(screen, (255, 255, 0), self.rect, width=1)

    def generate(self, x: int, y: int) -> dict:
        """Takes the chunk coordinates and returns a dictionary containing the block data inside the chunk"""

        seed(x*CHUNK_SIZE+y*CHUNK_SIZE)
        chunk_data = {}
        for y_pos in range(CHUNK_SIZE):
            for x_pos in range(CHUNK_SIZE):
                target = (x * CHUNK_SIZE + x_pos, y * CHUNK_SIZE + y_pos)
                block_name = ""

                # Cave noise map
                cave_noise_map_coords = [target[0]/70, target[1]/70]
                # Don't generate blocks if it satifies a certain range of values in the cave noise map, AKA a cave
                cave_noise_map_value = cave_generate(cave_noise_map_coords)

                if not (92.7 < cave_noise_map_value < 100):
                    # Generate terrain
                    height = terrain_generate(target[0])
                    if target[1] == height:
                        block_name = "grass_block"
                    elif height+1 <= target[1] < height+4:
                        block_name = "dirt"
                    elif target[1] >= height+4:
                        block_name = "stone"
                    if target[1] == height-1:
                        if not (92.7 < cave_generate([target[0]/70, (target[1]+1)/70]) < 100):
                            if randint(0, 2) == 0:
                                block_name = "grass"
                            if randint(0, 21) == 0:
                                block_name = choices(["poppy", "dandelion"], weights=[1, 2])[0]
                    if block_name != "":
                        chunk_data[target] = block_name

        # Generate structures
        generator = StructureGenerator("oak_tree", obstruction=False)
        chunk_data = generate_structures(x, y, chunk_data, generator, (1, 2))
        generator = StructureGenerator("tall_grass", obstruction=True)
        chunk_data = generate_structures(x, y, chunk_data, generator, (4, 3))
        return chunk_data

def terrain_generate(x: int) -> float:
    """Takes the x position of a block and returns the height it has to be at"""
    return -int(snoise.noise2(x*0.1, 0)*5)+5

def cave_generate(coords: list) -> float:
    """Takes the coordinates of a block and returns the noise map value for cave generation"""
    noise_height = pnoise(coords)
    noise_height = noise_height + 0.5 if noise_height > 0 else 0
    noise_height = int(pow(noise_height * 255, 0.9))
    return noise_height

def get_structures(x: int, y: int, generator: StructureGenerator, chance: tuple) -> list:
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
    seed(SEED + x * CHUNK_SIZE + y * CHUNK_SIZE)
    for _ in range(chance[0]):
        if randint(0, chance[1]) == 0:
            block_x = x * CHUNK_SIZE + randrange(0, CHUNK_SIZE)
            # Generate on the surface of the world
            grass_y = terrain_generate(block_x)-1

            # If it is cut off by a cave, don't generate
            if (92.7 < cave_generate([block_x/70, grass_y/70]) < 100) or (92.7 < cave_generate([block_x/70, (grass_y+1)/70]) < 100):
                return out
            # Structures that are not in this chunk
            if not 0 <= grass_y - y * CHUNK_SIZE < CHUNK_SIZE:
                return out

            out.append(generator.generate((block_x, grass_y)))
    return out

def generate_structures(x: int, y: int, chunk_data: dict, generator: StructureGenerator, chance: tuple) -> dict:
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
    chunk_data_orig = chunk_data.copy()
    # Check all chunks around the current chunk within the size limit of the structure
    for ox in range(-generator.chunks_to_check[0], generator.chunks_to_check[0] + 1):
        for oy in range(-generator.chunks_to_check[1], generator.chunks_to_check[1] + 1):
            # Get the surrounding structures that might protrude into the current chunk
            structs = get_structures(x + ox, y + oy, generator, chance)
            for struct in structs:
                for block, block_name in struct.items():
                    # If there are parts of that structure inside the current chunk, generate that part in this chunk
                    if 0 <= block[0]-x*CHUNK_SIZE < CHUNK_SIZE and 0 <= block[1]-y*CHUNK_SIZE < CHUNK_SIZE:
                        if block in chunk_data:
                            # Check if that position already has block and whether it can be overwritten by the structure
                            # i.e. leaves can replace grass but not grass blocks
                            if "overwriteable" in BLOCK_DATA[block_name]:
                                if chunk_data[block] in BLOCK_DATA[block_name]["overwriteable"]:
                                    chunk_data[block] = block_name
                                else:
                                    # Obstruction determines whether the struture can generate when there are non-overwriteable blocks in its way
                                    if generator.obstruction:
                                        return chunk_data_orig
                            else:
                                if not generator.obstruction:
                                    chunk_data[block] = block_name
                                else:
                                    return chunk_data_orig
                        else:
                            chunk_data[block] = block_name
    return chunk_data

def load_chunks(camera) -> list:
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
    
    # 103 lines of comments... maybe I went overboard xD
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

                # This might be:
                # structures["oak_tree"][short_oak_tree] = ((2, 4), {
                #     (0, 4): "oak_leaves",
                #     ect.
                # })
                structures[folder][struct[:-10]] = (origin, blocks)

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