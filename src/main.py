from random import randint, seed, choices, randrange
from math import ceil
from perlin_noise import PerlinNoise
import opensimplex
import json
import os
import time
import pygame
from pygame.locals import  (
    HWSURFACE, SRCALPHA, DOUBLEBUF,
    K_w, K_e, K_a, K_d,
    K_1, K_9, K_0, K_F5,
    MOUSEBUTTONDOWN, KEYDOWN,
    QUIT,
)

from constants import *
from utils import *
from images import *
from player import Player

def loading():
    font = pygame.font.Font(REGULAR_FONT_LOC, 120)
    textsurface = font.render("Generating World...", True, (255, 255, 255))
    screen.blit(textsurface, (50, 200))
    pygame.display.flip()

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50, 50)
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE | DOUBLEBUF)
pygame.display.set_caption("2D Minecraft")
loading()
clock = pygame.time.Clock()
mixer = pygame.mixer.init()
noise = opensimplex.OpenSimplex(seed=SEED)
pnoise = PerlinNoise(seed=SEED)
seed(SEED)

block_data = {}
for j in os.listdir("data/blocks/"):
    block_data[j[:-5]] = json.loads(open("data/blocks/"+j, "r").read())
structures = {}
for folder in os.listdir("data/structures/"):
    structures[folder] = {}
    for struct in os.listdir("data/structures/" + folder):
        if struct != "distribution.structure":
            data = open(f"data/structures/{folder}/{struct}", "r").readlines()
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
            distribution = open(f"data/structures/{folder}/distribution.structure", "r").readlines()
            weights = [int(d[:-2].split(" ")[1]) for d in distribution]
            files = [d[:-2].split(" ")[0] for d in distribution]
            structures[folder]["distribution"] = {"weights": weights, "files": files}

def remove_block(pos, data, neighbors):
    pos = inttup(pos)
    for _ in range(randint(18, 26)):
        Particle("block", VEC(pos)*BLOCK_SIZE+VEC(randint(0, BLOCK_SIZE), randint(0, BLOCK_SIZE)), master=blocks[pos])
    chunk = (pos[0] // CHUNK_SIZE, pos[1] // CHUNK_SIZE)
    if "next_layer" in data:
        blocks[pos] = Block(chunk, pos, data["next_layer"])
        chunks[chunk].block_data[pos] = data["next_layer"]
    else:
        del blocks[pos]
        del chunks[chunk].block_data[pos]
    for neighbor in neighbors:
        if neighbors[neighbor] in blocks:
            blocks[neighbors[neighbor]].update()

def set_block(pos, name, neighbors):
    pos = inttup(pos)
    chunk = (pos[0] // CHUNK_SIZE, pos[1] // CHUNK_SIZE)
    try:
        blocks[pos] = Block(chunks[chunk], pos, name)
        chunks[chunk].block_data[pos] = name
    except: pass
    for neighbor in neighbors:
        chunk = (neighbors[neighbor][0] // CHUNK_SIZE, neighbors[neighbor][1] // CHUNK_SIZE)
        if neighbors[neighbor] in blocks:
            blocks[neighbors[neighbor]].update()

def is_occupied(pos):
    pos = inttup(pos)
    if not pygame.Rect(VEC(pos)*BLOCK_SIZE, (BLOCK_SIZE, BLOCK_SIZE)).colliderect(pygame.Rect(player.pos, player.size)):
        if pos in blocks:
            return not "replaceable" in blocks[pos].data
        else:
            return False
    return True

def is_supported(pos, data, neighbors, c=False):
    if data["support"]:
        supports = data["support"]
        for support in supports:
            if inttup(support.split(" ")) != inttup(VEC(c)-VEC(pos)):
                if neighbors[support] in blocks:
                    if blocks[neighbors[support]].name not in supports[support]:
                        return False
                else:
                    return False
            else:
                return True
    return True

def is_placeable(pos, data, neighbors, c=False):
    if not is_occupied(pos) and is_supported(pos, data, neighbors, c=c):
        return True
    return False

class Particle(pygame.sprite.Sprite):
    def __init__(self, type, pos, master=None):
        pygame.sprite.Sprite.__init__(self)
        particles.append(self)
        self.type = type
        self.pos = VEC(pos)
        self.coords = self.pos // BLOCK_SIZE
        
        if self.type == "block":
            self.size = randint(6, 8)
            self.image = pygame.Surface((self.size, self.size))
            self.vel = VEC(randint(-35, 35)/10, randint(-30, 5)/10)
            if master:
                self.master = master
                color = self.master.image.get_at((randint(0, BLOCK_SIZE-1), randint(0, BLOCK_SIZE-1)))
                self.image.fill(color)
                if color == (255, 255, 255):
                    particles.remove(self)
                    self.kill()
                    
        self.timer = time.time()
        self.survive_time = randint(4, 8) / 10

    def update(self):
        if time.time() - self.timer > self.survive_time:
            particles.remove(self)
            self.kill()
            
        if inttup(self.coords) in blocks:
            if blocks[inttup(self.coords)].data["collision_box"] == "none":
                self.vel.y += GRAVITY * dt
        else:
            self.vel.y += GRAVITY * dt
        self.vel.x *= 0.93
        
        neighbors = [
            inttup(self.coords),
            inttup((self.coords.x-1, self.coords.y)),
            inttup((self.coords.x+1, self.coords.y)),
            inttup((self.coords.x, self.coords.y-1)),
            inttup((self.coords.x, self.coords.y+1)),
        ]
        for pos in neighbors:
            if pos in blocks:
                block = blocks[pos]
                if block.data["collision_box"] != "none":
                    if pygame.Rect(block.pos.x, block.pos.y, BLOCK_SIZE, BLOCK_SIZE).collidepoint(self.pos.x+self.vel.x*dt, self.pos.y):
                        self.vel.x = 0
                        break
                    if pygame.Rect(block.pos.x, block.pos.y, BLOCK_SIZE, BLOCK_SIZE).collidepoint(self.pos.x, self.pos.y+self.vel.y*dt):
                        self.vel.y = 0
                        break
                    
        self.pos += self.vel * dt
        self.coords = self.pos // BLOCK_SIZE
        
        if inttup(self.coords // CHUNK_SIZE) not in rendered_chunks:
            try: particles.remove(self)
            except: pass
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, (self.pos-player.camera.pos-VEC(self.image.get_size())/2))
        
class Block(pygame.sprite.Sprite):
    def __init__(self, chunk, pos, name):
        pygame.sprite.Sprite.__init__(self)
        blocks[tuple(pos)] = self
        self.name = name
        self.data = block_data[self.name]
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
        
        if self.data["collision_box"] == "full":
            self.rect = pygame.Rect(self.pos, (BLOCK_SIZE, BLOCK_SIZE))
        elif self.data["collision_box"] == "none":
            self.rect = pygame.Rect(self.pos, (0, 0))

    def update(self):
        if not is_supported(self.pos, self.data, self.neighbors):
            remove_blocks.append(self.coords)

    def draw(self, screen):
        self.rect.topleft = self.pos - player.camera.pos
        screen.blit(self.image, self.rect.topleft)

class Chunk(object):
    def __init__(self, pos):
        self.pos = pos
        self.block_data = generate_chunk(pos[0], pos[1])
        chunks[self.pos] = self

    def render(self):
        if self.pos in rendered_chunks:
            for block in self.block_data:
                if not block in blocks:
                    blocks[block] = Block(self, block, self.block_data[block])
                blocks[block].draw(screen)

    def debug(self):
        pygame.draw.rect(screen, (255, 255, 0), (self.pos[0]*CHUNK_SIZE*BLOCK_SIZE-player.camera.pos[0], self.pos[1]*CHUNK_SIZE*BLOCK_SIZE-player.camera.pos[1], CHUNK_SIZE*BLOCK_SIZE, CHUNK_SIZE*BLOCK_SIZE), width=1)

class StructureGenerator(object):
    def __init__(self, folder, obstruction=False):
        self.folder = folder
        self.obstruction = obstruction
        self.files = structures[folder]
        self.distribution = structures[folder]["distribution"]
        self.block_data = {}
        
        max_sizes = []
        for file in self.files:
            if file != "distribution":
                self.block_data[file] = structures[folder][file]
                max_sizes.append((max(x for x, y in self.block_data[file][1]) - min(x for x, y in self.block_data[file][1]) + 1,
                            max(y for x, y in self.block_data[file][1]) - min(y for x, y in self.block_data[file][1]) + 1))
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
            for offset, block in self.block_data[file][1].items()
        }
        
        return block_data

class Crosshair():
    """The class responsible for the drawing and updating of the crosshair"""

    def __init__(self, changespeed: int) -> None:
        """Creates a crosshair object"""

        self.color = pygame.Color(0, 0, 0)
        self.changeover = changespeed
        
    def update(self, mpos: pygame.math.Vector2) -> None:
        """Update the crosshair"""

        color = self.get_avg_color(mpos)
        if 127-30 < color.r < 127+30 and 127-30 < color.g < 127+30 and 127-30 < color.b < 127+30:
            color = pygame.Color(255, 255, 255)
        color = pygame.Color(255, 255, 255) - color

        # Modified version of this SO answer, thank you!
        # https://stackoverflow.com/a/51979708/17303382
        self.color = [x + (((y - x) / self.changeover) * 100 * dt) for x, y in zip(self.color, color)]

    def draw(self, screen: pygame.surface.Surface, mpos: pygame.math.Vector2) -> None:
        """Draw the crosshair to the screen"""

        pygame.draw.rect(screen, self.color, (mpos[0]-2, mpos[1]-16, 4, 32))
        pygame.draw.rect(screen, self.color, (mpos[0]-16, mpos[1]-2, 32, 4))

    def get_avg_color(self, mpos: pygame.math.Vector2) -> pygame.Color:
        """Gets the average colour of the screen at the crosshair using the position of the mouse

        Returns:
            pygame.Color: The average colour at the position of the crosshair
        """

        try:
            surf = screen.subsurface((mpos[0]-16, mpos[1]-16, 32, 32))
            color = pygame.Color(pygame.transform.average_color(surf))
        except:
            try:
                color = screen.get_at(inttup(mpos))
            except:
                color = pygame.Color(255, 255, 255)

        return color

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
                            if "overwriteable" in block_data[block_name]:
                                if chunk_data[block] in block_data[block_name]["overwriteable"]:
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

def terrain_generate(x: int) -> float:
    """Takes the x position of a block and returns the height it has to be at"""
    return -int(noise.noise2(x*0.1, 0)*5)+5

def cave_generate(coords: list) -> float:
    """Takes the coordinates of a block and returns the noise map value for cave generation"""
    noise_height = pnoise(coords)
    noise_height = noise_height + 0.5 if noise_height > 0 else 0
    noise_height = int(pow(noise_height * 255, 0.9))
    return noise_height

def generate_chunk(x: int, y: int) -> dict:
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

blocks = {}
chunks = {}
player = Player()
crosshair = Crosshair(1750)
particles = []
player.inventory.add_item("grass_block")
player.inventory.add_item("dirt")
player.inventory.add_item("stone")
player.inventory.add_item("grass")
player.inventory.add_item("oak_log")
player.inventory.add_item("oak_leaves")
player.inventory.add_item("oak_planks")
player.inventory.add_item("cobblestone")
player.inventory.add_item("glass")
player.inventory.add_item("poppy")
player.inventory.add_item("dandelion")
player.inventory.add_item("tall_grass")

pygame.mouse.set_visible(False)
remove_blocks = []

def draw(screen):
    screen.fill((135, 206, 250))
    mpos = VEC(pygame.mouse.get_pos())
    block_pos = (player.pos+(mpos-player.rect.topleft))//BLOCK_SIZE
    for chunk in rendered_chunks:
        chunks[chunk].render()
    for particle in particles:
        particle.draw(screen)
    player.draw(screen)
    
    # Debug stuff
    if debug:
        for chunk in rendered_chunks:
            chunks[chunk].debug()
        pygame.draw.rect(screen, (255, 255, 255), player.rect, width=1)
        for rect in player.detecting_rects:
            pygame.draw.rect(screen, (255, 0, 0), rect, width=1)
        screen.blit(text(f"Seed: {SEED}"), (6, 0))
        screen.blit(text(f"Velocity: {(round(player.vel.x, 3), round(player.vel.y, 3))}"), (6, 24))
        screen.blit(text(f"Position: {inttup(player.coords)}"), (6, 48))
        screen.blit(text(f"Camera offset: {inttup(player.pos-player.camera.pos-VEC(SCR_DIM)/2+player.size/2)}"), (6, 72))
        screen.blit(text(f"Chunk: {inttup(player.coords//CHUNK_SIZE)}"), (6, 96))
        screen.blit(text(f"Chunks loaded: {len(chunks)}"), (6, 120))
        screen.blit(text(f"Rendered blocks: {len(blocks)}"), (6, 144))
        if not player.inventory.visible:
            if inttup(block_pos) in blocks:
                screen.blit(text(f"{blocks[inttup(block_pos)].name.replace('_', ' ')}", color=(255, 255, 255)), (mpos[0]+12, mpos[1]-36))
    
    player.inventory.draw(screen)
    if not player.inventory.visible:
        crosshair.draw(screen, mpos)

    pygame.display.flip()

running = True
debug = False

while running:
    dt = clock.tick_busy_loop(FPS) / 16
    if dt > 12: dt = 12
    pygame.display.set_caption(f"2D Minecraft | FPS: {int(clock.get_fps())}")
    
    mpos = VEC(pygame.mouse.get_pos())

    mouse_state = 0
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            
        if event.type == MOUSEBUTTONDOWN:
            mouse_state = event.button
            if not player.inventory.visible:
                block_pos = inttup((player.pos+(mpos-player.rect.topleft))//BLOCK_SIZE)
                neighbors = {
                    "0 -1": inttup((block_pos[0], block_pos[1]-1)),
                    "0 1": inttup((block_pos[0], block_pos[1]+1)),
                    "-1 0": inttup((block_pos[0]-1, block_pos[1])),
                    "1 0": inttup((block_pos[0]+1, block_pos[1]))
                }
                
                if event.button == 1:
                    if block_pos in blocks:
                        remove_block(block_pos, blocks[block_pos].data, neighbors)
                        
                if event.button == 3:
                    if player.holding:
                        if "counterparts" in block_data[player.holding]:
                            counterparts = block_data[player.holding]["counterparts"]
                            for counterpart in counterparts:
                                c_pos = VEC(block_pos)+VEC(inttup(counterpart.split(" ")))
                                c_neighbors = {
                                    "0 -1": inttup((c_pos.x, c_pos.y-1)),
                                    "0 1": inttup((c_pos.x, c_pos.y+1)),
                                    "-1 0": inttup((c_pos.x-1, c_pos.y)),
                                    "1 0": inttup((c_pos.x+1, c_pos.y))
                                }
                                if not is_placeable(c_pos, block_data[counterparts[counterpart]], c_neighbors, c=block_pos):
                                    break
                            else:
                                for counterpart in counterparts:
                                    if not is_placeable(block_pos, block_data[player.holding], neighbors, c=c_pos):
                                        break
                                else:
                                    set_block(block_pos, player.holding, neighbors)
                                    for counterpart in counterparts:
                                        c_pos = VEC(block_pos)+VEC(inttup(counterpart.split(" ")))
                                        c_neighbors = {
                                            "0 -1": inttup((c_pos.x, c_pos.y-1)),
                                            "0 1": inttup((c_pos.x, c_pos.y+1)),
                                            "-1 0": inttup((c_pos.x-1, c_pos.y)),
                                            "1 0": inttup((c_pos.x+1, c_pos.y))
                                        }
                                        set_block(VEC(block_pos)+VEC(inttup(counterpart.split(" "))), counterparts[counterpart], c_neighbors)
                        else:
                            if is_placeable(block_pos, block_data[player.holding], neighbors):
                                set_block(block_pos, player.holding, neighbors)
                                
        if event.type == KEYDOWN:
            if event.key == K_F5:
                debug = not debug
            if event.key == K_e:
                player.inventory.visible = not player.inventory.visible
                if player.inventory.visible:
                    pygame.mouse.set_visible(True)
                else:
                    pygame.mouse.set_visible(False)
                    if player.inventory.selected:
                        player.inventory.add_item(player.inventory.selected.name)
                        player.inventory.selected = None

    rendered_chunks = []
    for y in range(int(HEIGHT/(CHUNK_SIZE*BLOCK_SIZE)+2)):
        for x in range(int(WIDTH/(CHUNK_SIZE*BLOCK_SIZE)+2)):
            chunk = (
                x - 1 + int(round(player.camera.pos.x / (CHUNK_SIZE * BLOCK_SIZE))),
                y - 1 + int(round(player.camera.pos.y / (CHUNK_SIZE * BLOCK_SIZE)))
            )
            rendered_chunks.append(chunk)
            if chunk not in chunks:
                chunks[chunk] = Chunk(chunk)
                
    unrendered_chunks = []
    for y in range(int(HEIGHT/(CHUNK_SIZE*BLOCK_SIZE)+4)):
        for x in range(int(WIDTH/(CHUNK_SIZE*BLOCK_SIZE)+4)):
            chunk = (
                x - 2 + int(round(player.camera.pos.x / (CHUNK_SIZE * BLOCK_SIZE))),
                y - 2 + int(round(player.camera.pos.y / (CHUNK_SIZE * BLOCK_SIZE)))
            )
            if chunk in chunks:
                if chunk not in rendered_chunks:
                    unrendered_chunks.append(chunk)
                    
    for chunk in unrendered_chunks:
        for block in chunks[chunk].block_data:
            if block in blocks:
                blocks[block].kill()
                del blocks[block]
                
    for block in remove_blocks:
        neighbors = {
            "0 -1": inttup((block[0], block[1]-1)),
            "0 1": inttup((block[0], block[1]+1)),
            "-1 0": inttup((block[0]-1, block[1])),
            "1 0": inttup((block[0]+1, block[1]))
        }
        remove_block(block, blocks[inttup(block)].data, neighbors)
        
    remove_blocks = []
    detecting_rects = []

    player.update(blocks, mouse_state, dt)
    for particle in particles:
        particle.update()
    crosshair.update(mpos)
    
    draw(screen)

pygame.quit()
quit()
