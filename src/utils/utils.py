# 2DMC is a passion project to recreate the game "Minecraft" (all credit to Mojang Studios) in 2D.
# Copyright (C) 2022 Doubleface
# You can view the terms of the GPL License in LICENSE.md

# The majority of the game assets are properties of Mojang Studios,
# you can view their TOS here: https://account.mojang.com/documents/minecraft_eula

from pygame.locals import SRCALPHA
from pstats import SortKey, Stats
from typing import Callable, Any
from datetime import datetime
from cProfile import Profile
from pathlib import Path
from os.path import join
from enum import Enum
import pygame

from src.utils.constants import PROFILES, VEC, BLOCK_SIZE

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

def filled_surf(size, color, tags=SRCALPHA):
    surf = pygame.Surface(size, tags)
    surf.fill(color)
    return surf

class SliceDarken(Enum):
    BACKGROUND = 0.72
    MIDDLEGROUND = 0.86
    FOREGROUND = 1

class PosDict(dict):
    """Custom dictionary that can take Vectors and turn them into tuples for hashing"""
    def __getitem__(self, key):
        return super().__getitem__(inttup(key))

    def __setitem__(self, key, value):
        super().__setitem__(inttup(key), value)

    def __delitem__(self, key):
        return super().__delitem__(inttup(key))

    def __contains__(self, key):
        return super().__contains__(inttup(key))
    
    def __missing__(self, key):
        return

def inttup(tup: tuple[int | float, int | float]) -> tuple[int, int]:
    return (int(tup[0]), int(tup[1]))

def scale_by(surf, scale):
    return pygame.transform.scale(surf, (surf.get_width() * scale, surf.get_height() * scale))

def sign(num: int | float) -> int:
    """Returns the sign of the num (+/-) as -1, 0, or 1"""
    return (num > 0) - (num < 0)

def pairing(count, *args: int) -> int:
    count -= 1
    if count == 0: return int(args[0])
    a = 2 * args[0] if args[0] >= 0 else -2 * args[0] - 1
    b = 2 * args[1] if args[1] >= 0 else -2 * args[1] - 1
    new = [0.5 * (a + b) * (a + b + 1) + b] + [num for i, num in enumerate(args) if i > 1]
    return pairing(count, *new)

def PPS(blocks: int | float | VEC) -> int | float | VEC:
    """Returns pixels per second equivalent of the input value in blocks per second"""
    return blocks * BLOCK_SIZE

def BPS(pixels: int | float | VEC) -> int | float | VEC:
    """Returns blocks per second equivalent of the input value in pixels per second"""
    return pixels / BLOCK_SIZE

do_profile = False
def profile(callable: Callable[..., Any], *args: tuple[Any]) -> Any:
    """Profiles the given callable and saves + prints the results
    Args:
        callable (type): A callabale type (function, constructor, ect)
    Returns:
        [...]: The result of calling the callable
    """

    global do_profile
    if do_profile: # Profile_bool stops the user from being able to hold down the profile key
        do_profile = False
        with Profile() as profile: # Profiling the contents of the with block
            returnval = callable(*args)     # Calling the callable with the args

        # Naming the profile file in the format "profile_{hour}-{minute}-{second}.prof"
        statfile = Path(join(PROFILES, str(datetime.now().strftime("profile_%H-%M-%S")) + ".prof"))
        if not (statfile_dirpath := statfile.parent).exists():
            statfile_dirpath.mkdir() # Creating the dirpath of the statfile (ex. "dev/profiles") if they do not exist

        stats = Stats(profile).sort_stats(SortKey.TIME) # Sorting the stats from highest time to lowest
        stats.dump_stats(filename=str(statfile)) # Saving the stats to a profile file
        stats.print_stats()                      # Printing the stats
        print(f"\n\n Profile saved to: {str(statfile)}!\n\n")
        return returnval
    else: # Return the output of the callable
        return callable(*args)