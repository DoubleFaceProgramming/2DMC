from pygame.draw import rect as drawrect
from random import randint, seed, choices, randrange
from pygame import Rect
from opensimplex import OpenSimplex
from perlin_noise import PerlinNoise
from math import ceil
from os import listdir
from os.path import join

from src.constants import CHUNK_SIZE, BLOCK_SIZE, SEED
from src.block import Block, BLOCK_DATA
from src.utils import pathof

snoise = OpenSimplex(seed=SEED)
pnoise = PerlinNoise(seed=SEED)

class StructureGenerator(object):
    def __init__(self, folder, obstruction=False):
        self.folder = folder
        self.obstruction = obstruction
        self.files = structures[folder]
        self.distribution = structures[folder]["distribution"]
        self.BLOCK_DATA = {}
        
        max_sizes = []
        for file in self.files:
            if file != "distribution":
                self.BLOCK_DATA[file] = structures[folder][file]
                max_sizes.append((max(x for x, y in self.BLOCK_DATA[file][1]) - min(x for x, y in self.BLOCK_DATA[file][1]) + 1,
                            max(y for x, y in self.BLOCK_DATA[file][1]) - min(y for x, y in self.BLOCK_DATA[file][1]) + 1))
        self.max_size = max(max_sizes)
        
        self.chunks_to_check = int(ceil(self.max_size[0] / CHUNK_SIZE)), int(ceil(self.max_size[1] / CHUNK_SIZE))

    def generate(self, origin):
        seed(SEED + origin[0] * CHUNK_SIZE + origin[1] * CHUNK_SIZE)
        file = choices(self.distribution["files"], weights=self.distribution["weights"])[0]
        mirror = randint(0, 1)
        
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
    
    def __init__(self, pos):
        self.pos = pos
        self.block_data = self.generate(pos[0], pos[1])
        self.__class__.instances[self.pos] = self
        self.rect = Rect(0, 0, 0, 0)
        
    def update(self, camera) -> None:
        self.rect.topleft = (self.pos[0] * CHUNK_SIZE * BLOCK_SIZE - camera.pos[0], 
                             self.pos[1] * CHUNK_SIZE * BLOCK_SIZE - camera.pos[1])

    def draw(self, camera, screen) -> None:
        #if self.pos in rendered_chunks:
        for block in self.block_data:
            if not block in Block.instances:
                Block.instances[block] = Block(self, block, self.block_data[block]) # !
            Block.instances[block].draw(camera, screen)

    def debug(self, screen) -> None:
        """Draws a debug rect around the chunk borders. Only called when global variable 'debug' is true."""
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

def load_structures() -> dict:
    structures = {}
    for folder in listdir(pathof("data/structures/")):
        structures[folder] = {}
        for struct in listdir(join(pathof("data/structures/"), folder)):
            if struct != "distribution.structure":
                data = open(pathof(f"data/structures/{folder}/{struct}"), "r").readlines()
                split = data.index("structure:\n")
                split2 = data.index("origin:\n")
                legends = {legend.split(":")[0]: legend.split(":")[1] for legend in [legend[:-1] for legend in data[:split]]}
                structure = [line[:-1] for line in data[split+1:split2]]
                origin = (int(data[-1].split(" ")[0]), int(data[-1].split(" ")[1]))
                blocks = {}
                for y in range(len(structure)):
                    for x in range(len(structure[y])):
                        try: legends[structure[y][x]]
                        except: pass
                        else: blocks[(x-origin[0], y-origin[1])] = legends[structure[y][x]]
                structures[folder][struct[:-10]] = (origin, blocks)
            else:
                distribution = open(pathof(f"data/structures/{folder}/distribution.structure"), "r").readlines()
                weights = [int(d[:-2].split(" ")[1]) for d in distribution]
                files = [d[:-2].split(" ")[0] for d in distribution]
                structures[folder]["distribution"] = {"weights": weights, "files": files}
    return structures
            
structures = load_structures()