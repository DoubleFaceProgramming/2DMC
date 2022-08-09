from enum import Enum, auto
from pygame import Surface

from constants import *

inttup = lambda tup: tuple((int(tup[0]), int(tup[1])))
intvec = lambda vec: VEC((int(vec[0]), int(vec[1])))

def pairing(count, *args: int) -> int:
    count -= 1
    if count == 0: return int(args[0])
    a = 2 * args[0] if args[0] >= 0 else -2 * args[0] - 1
    b = 2 * args[1] if args[1] >= 0 else -2 * args[1] - 1
    new = [0.5 * (a + b) * (a + b + 1) + b] + [num for i, num in enumerate(args) if i > 1]
    return pairing(count, *new)

def filled_surf(size, color, tags=SRCALPHA):
    surf = Surface(size, tags)
    surf.fill(color)
    return surf

class AutoEnum(Enum):
    def __new__(cls):
        value = len(cls.__members__)
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

class WorldSlices(AutoEnum):
    BACKGROUND = ()
    MIDDLEGROUND = ()
    FOREGROUND = ()

class SliceOverlay(Enum):
    BACKGROUND = filled_surf((BLOCK_SIZE, BLOCK_SIZE), (0, 0, 0, 70))
    MIDDLEGROUND = filled_surf((BLOCK_SIZE, BLOCK_SIZE), (0, 0, 0, 40))
    FOREGROUND = Surface((0, 0))

class PosDict(dict):
    """Custom dictionary that can take Vectors and turn them into tuples for hashing, doesn't error if key doesn't exist"""
    def __getitem__(self, key):
        return super().__getitem__(inttup(key))

    def __setitem__(self, key, value):
        super().__setitem__(inttup(key), value)

    def __delitem__(self, key):
        return super().__delitem__(inttup(key))

    def __contains__(self, key):
        return super().__contains__(inttup(key))

    def __missing__(self, key):
        return ""