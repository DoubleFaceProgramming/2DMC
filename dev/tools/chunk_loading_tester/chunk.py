from __future__ import annotations
from msilib.schema import Feature
from tracemalloc import start
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_manager import GameManager

from random import randint, choice
from random import seed as rseed
from typing import Generator
from numpy import ndarray
import pygame

from features import StoneBlob, Feature
from block import Location, Block
from sprite import LayersEnum
from sprite import Sprite
from constants import *
from utils import *

def generate_location(coords: tuple[int, int], cave: bool) -> tuple[str | None, str | None, str | None]:
    """Generate the names of the blocks to go at a certain location. Temporary world gen!"""

    coords = VEC(coords)
    if coords.y == 4:
        name = "grass_block"
    elif 4 < coords.y <= 8:
        name = "dirt"
    elif coords.y > 8:
        name = "stone"
    else:
        name = None

    # Only generate the background is theres a cave
    return (name,) if cave else (name, name)

class ChunkData(PosDict):
    """Custom dictionary that also has methods that handle chunk generation"""
    def __init__(self, manager: GameManager, master: Chunk, chunk_pos: tuple[int, int] | VEC) -> None:
        self.manager = manager
        self.scene = self.manager.scene
        self.master = master
        self.chunk_pos = VEC(chunk_pos)
        self.generate_base()
        self.populate_features()

    def iterate(self) -> Generator:
        """Iterates through every coordinate inside the chunk, yields the absolute coordinates AND chunk coordinates"""
        for y in range(CHUNK_SIZE):
            for x in range(CHUNK_SIZE):
                yield (x + self.chunk_pos.x * CHUNK_SIZE, y + self.chunk_pos.y * CHUNK_SIZE), (x, y)

    def generate_cave_map(self) -> ndarray:
        """Creates a numpy ndarray storing the heightmap for cave generation"""
        return self.scene.noise.genAsGrid([CHUNK_SIZE, CHUNK_SIZE, 1], [int(self.chunk_pos.x * CHUNK_SIZE), int(self.chunk_pos.y * CHUNK_SIZE), 0]).tolist()
    
    def is_cave(self, pos: tuple | VEC) -> bool:
        """Determines if a position is in a cave based on the noise map"""
        return -0.55 < self.noise_map[pos[0]][pos[1]][0] < -0.48

    def generate_base(self) -> None:
        """Generate every block in the chunk"""
        rseed(pairing(3, *self.chunk_pos, SEED))
        self.noise_map = self.generate_cave_map()
        for pos, in_chunk_pos in self.iterate():
            self[pos] = Location(self.master, pos, *generate_location(pos, self.is_cave(in_chunk_pos)))

    # TODO: In the future, use BiomeData class which stores information of biomes including what features to generate and how in each biome
    def populate_features(self) -> None:
        positions = [(randint(self.chunk_pos.x * CHUNK_SIZE, self.chunk_pos.x * CHUNK_SIZE + CHUNK_SIZE - 1), randint(self.chunk_pos.y * CHUNK_SIZE, self.chunk_pos.y * CHUNK_SIZE + CHUNK_SIZE - 1)) for _ in range(randint(0, 2))]
        for start_pos in positions:
            start_pos = VEC(start_pos)
            seed = pairing(3, *start_pos, SEED)
            rseed(seed)
            generator = StoneBlob(seed, choice(["andesite", "diorite", "granite"]))
            feature = Feature(generator())
            for pos, block_name in feature.generator:
                if start_pos + pos in self:
                    location = self[start_pos + pos]
                    location[WorldSlices.MIDDLEGROUND] = Block(location, block_name, WorldSlices.MIDDLEGROUND)

class Chunk(Sprite):
    instances = PosDict()

    def __init__(self, manager: GameManager, chunk_pos: tuple[int, int] | VEC, chunk_data=None) -> None:
        super().__init__(manager, LayersEnum.CHUNKS)
        self.__class__.instances[chunk_pos] = self
        self.chunk_pos = VEC(chunk_pos)
        if not chunk_data:
            self.chunk_data = ChunkData(self.manager, self, self.chunk_pos)
        else:
            self.chunk_data = chunk_data
        self.image = pygame.Surface((CHUNK_PIXEL_SIZE, CHUNK_PIXEL_SIZE), SRCALPHA)
        # Updates every location on the chunk as the chunk was just created
        for coords, location in self.chunk_data.items():
            self.update_image(VEC(coords), location.image, first=True)

    def update_image(self, coords: tuple[int, int], image: pygame.Surface, first: bool = False) -> None:
        """Update the image of a location on it's parent chunk."""
        on_chunk_pos = (coords.x % CHUNK_SIZE * BLOCK_SIZE, coords.y % CHUNK_SIZE * BLOCK_SIZE)
        if not first:
            self.image.fill((0, 0, 0, 0), (*on_chunk_pos, BLOCK_SIZE, BLOCK_SIZE)) # Clear the area that the image occupies
        self.image.blit(image, on_chunk_pos)

    def draw(self) -> None:
        self.manager.screen.blit(self.image, self.chunk_pos * CHUNK_PIXEL_SIZE)
        pygame.draw.rect(self.manager.screen, (255, 255, 0), (self.chunk_pos * CHUNK_PIXEL_SIZE, self.image.get_size()), 1)

    def kill(self) -> None:
        del self.__class__.instances[self.chunk_pos]
        super().kill()