import pygame
import json
import os

from src.constants import *
from src.utils import *
from src.images import *
from src.particle import Particle

BLOCK_DATA = {}
for j in os.listdir(pathof("data/blocks/")):
    BLOCK_DATA[j[:-5]] = json.loads(open(os.path.join(pathof("data/blocks/"), j), "r").read())

class Block(pygame.sprite.Sprite):
    instances = {}
    
    def __init__(self, chunk, pos, name):
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
        
        if self.data["collision_box"] == "full":
            self.rect = pygame.Rect(self.pos, (BLOCK_SIZE, BLOCK_SIZE))
        elif self.data["collision_box"] == "none":
            self.rect = pygame.Rect(self.pos, (0, 0))

    def update(self):
        if not is_supported(self.pos, self.data, self.neighbors):
            # remove_blocks.append(self.coords)
            # if inttup(self.pos) in self.__class__.instances:
            del self.__class__.instances[inttup(self.pos)]
            del self

    def draw(self, camera, screen):
        self.rect.topleft = self.pos - camera.pos
        screen.blit(self.image, self.rect.topleft)

def remove_block(chunks, pos, data, neighbors):
    pos = inttup(pos)
    for _ in range(randint(18, 26)):
        Particle("block", VEC(pos)*BLOCK_SIZE+VEC(randint(0, BLOCK_SIZE), randint(0, BLOCK_SIZE)), master=Block.instances[pos])
    chunk = (pos[0] // CHUNK_SIZE, pos[1] // CHUNK_SIZE)
    if "next_layer" in data:
        Block.instances[pos] = Block(chunk, pos, data["next_layer"])
        chunks[chunk].block_data[pos] = data["next_layer"]
    else:
        del Block.instances[pos]
        del chunks[chunk].block_data[pos]
    for neighbor in neighbors:
        if neighbors[neighbor] in Block.instances:
            Block.instances[neighbors[neighbor]].update()

def set_block(chunks, pos, name, neighbors):
    pos = inttup(pos)
    chunk = (pos[0] // CHUNK_SIZE, pos[1] // CHUNK_SIZE)
    try:
        Block.instances[pos] = Block(chunks[chunk], pos, name)
        chunks[chunk].block_data[pos] = name
    except: pass
    for neighbor in neighbors:
        chunk = (neighbors[neighbor][0] // CHUNK_SIZE, neighbors[neighbor][1] // CHUNK_SIZE)
        if neighbors[neighbor] in Block.instances:
            Block.instances[neighbors[neighbor]].update()

def is_occupied(player, pos):
    pos = inttup(pos)
    if not pygame.Rect(VEC(pos) * BLOCK_SIZE, (BLOCK_SIZE, BLOCK_SIZE)).colliderect(pygame.Rect(player.pos, player.size)):
        if pos in Block.instances:
            return not "replaceable" in Block.instances[pos].data
        else:
            return False
    return True

def is_supported(pos, data, neighbors, c=False):
    if data["support"]:
        supports = data["support"]
        for support in supports:
            if inttup(support.split(" ")) != inttup(VEC(c)-VEC(pos)):
                if neighbors[support] in Block.instances:
                    if Block.instances[neighbors[support]].name not in supports[support]:
                        return False
                else:
                    return False
            else:
                return True
    return True

def is_placeable(player, pos, data, neighbors, c=False):
    if not is_occupied(player, pos) and is_supported(pos, data, neighbors, c=c):
        return True
    return False