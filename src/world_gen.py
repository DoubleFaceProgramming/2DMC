from random import randint, seed, choices, choice, randrange
from pygame.draw import rect as drawrect
from perlin_noise import PerlinNoise
from opensimplex import OpenSimplex
from pygame import Rect, Surface
from os.path import join
from pathlib import Path
from os import listdir
from math import ceil
import time

from src.constants import CHUNK_SIZE, BLOCK_SIZE, SEED, WIDTH, HEIGHT
from src.block import Block, BLOCK_DATA
from src.player import Camera
from src.utils import ascii_str_sum, canter_pairing, pathof

seed(SEED)
snoise = OpenSimplex(seed=SEED)
pnoise = PerlinNoise(seed=SEED)

class Chunk(object):
    """The class responsible for updating and drawing chunks."""
    instances = {}

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

        start = time.time()

        seed(SEED + canter_pairing((x, y)))
        chunk_data = {}
        for y_pos in range(CHUNK_SIZE):
            for x_pos in range(CHUNK_SIZE):
                block_pos = (x * CHUNK_SIZE + x_pos, y * CHUNK_SIZE + y_pos)
                # Generate each block
                block_name = generate_block(block_pos[0], block_pos[1])

                if block_name != "":
                    chunk_data[block_pos] = block_name

        print(time.time() - start)

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

def generate_block(x, y):
    # Cave noise map
    cave_noise_map_coords = [x/70, y/70]
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
            if not (92.7 < cave_generate([x/70, (y+1)/70]) < 100):
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

# oak_tree_gen = StructureGenerator("oak_tree")
# tall_grass_gen = StructureGenerator("tall_grass", obstruction=True)
# granite_gen = BlobGenerator("granite", (10, 10), 5, 3, obstruction=True)
# diorite_gen = BlobGenerator("diorite", (10, 10), 5, 3, obstruction=True)
# andesite_gen = BlobGenerator("andesite", (10, 10), 5, 3, obstruction=True)
# coal_ore_gen = BlobGenerator("coal_ore", (8, 4), 4, 2)
# iron_ore_gen = BlobGenerator("iron_ore", (3, 4), 4, 1)
# gold_ore_gen = BlobGenerator("gold_ore", (3, 3), 4, 1)
# lapis_lazuli_ore_gen = BlobGenerator("lapis_lazuli_ore", (3, 3), 4, 1)
# redstone_ore_gen = BlobGenerator("redstone_ore", (3, 3), 4, 1)
# diamond_ore_gen = BlobGenerator("diamond_ore", (3, 3), 4, 1)
# emerald_ore_gen = BlobGenerator("emerald_ore", (2, 2), 1, 1)