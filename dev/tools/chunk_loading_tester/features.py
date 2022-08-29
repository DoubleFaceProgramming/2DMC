from abc import abstractmethod
from typing import Generator, Any

from metaball import blob

from constants import CHUNK_SIZE
from utils import BlobParams

class Feature:
    instances = {}

    def __init__(self, generator) -> None:
        self.generator = generator

class FeatureGenerator:
    def __init__(self, seed: int) -> None:
        self.seed = seed
        self.name = self.__class__.__name__

    @abstractmethod
    def __call__(self) -> Generator:
        pass

class StoneBlob(FeatureGenerator):
    def __init__(self, seed: int, block_name: str) -> None:
        self.type = block_name
        super().__init__(seed)

    def __call__(self) -> Generator:
        for pos in blob(self.seed, *BlobParams.NATURAL_STONE.value):
            yield (pos, self.type)