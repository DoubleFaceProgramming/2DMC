from pygame.draw import rect as drawrect
from pygame.locals import SRCALPHA
from pygame.surface import Surface
from pygame.math import Vector2
from random import random
from pathlib import Path
from pygame import Rect
from typing import Any
import datetime
import cProfile
import pstats
import os

from src.constants import VEC, FONT20, FONT24, BLOCK_SIZE, PROFILE_DIR

class CyclicalList:
    def __init__(self, elements: list[Any], start: int = 0) -> None:
        self.elements = list(elements)
        self.current = self.elements[start]
        self.index = start

        # What % len(self) does is that if adding the amount goes over the length of the list, it would wrap around
        self.calc_index = lambda amount: (self.index + amount) % len(self)

    def __iadd__(self, amount: int):
        self.index = self.calc_index(amount)
        self.current = self[self.index] # We have __getitem__ overloaded so we can do self[]

        return self

    def __len__(self) -> int:
        return len(self.elements)

    def __isub__(self, amount: int):
        self.index = self.calc_index(-amount)
        self.current = self[self.index] # We have __getitem__ overloaded so we can do self[]

        return self

    def __getitem__(self, key: int) -> Any:
        return self.elements[key]

    def __setitem__(self, key: int, value: Any) -> None:
        self.elements[key] = value

    def __delitem__(self, key) -> None:
        del self.elements[key]

    def __iter__(self):
        return self

    def __next__(self):
        self.__iadd__(1)
        return self.current

def intv(vector: Vector2) -> Vector2:
    """Returns vector where x and y are integers"""
    return VEC(int(vector.x), int(vector.y))

def inttup(tup: tuple[float, float] | VEC) -> tuple:
    """Returns a tuple where both elements are integers"""
    return (int(tup[0]), int(tup[1]))

def text(text: str, color: tuple=(0, 0, 0)) -> Surface:
    """Returns a surface which has the given text argument rendered using font 24 in the given colour (default black)"""
    return FONT24.render(text, True, color)

def smol_text(text: str, color: tuple=(255, 255, 255)) -> Surface:
    """Returns a surface which has the given text argument rendered using font 20 in the given colour (default white)"""
    return FONT20.render(text, True, color)

def create_text_box(text: Surface, pos: tuple, opacity: int) -> tuple[Surface, tuple]:
    """Creats a text box at the position given with the supplied text and opacity

    Args:
        text (Surface): A rendered surface of the text (most often generated by text())
        pos (tuple): The position to draw at
        opacity (int): The opacity of the text box

    Returns:
        tuple[Surface, tuple]: Returns a surface containing the text box and the position to draw at
    """
    # Creating a surface slightly larger than the text and changing opacity
    text_rect = text.get_rect()
    blit_pos = pos
    surface = Surface((text_rect.width+16, text_rect.height+8), SRCALPHA)
    surface.set_alpha(opacity)

    # Drawing a bunch of rects the make the minecraft-y style purple border
    drawrect(surface, (0, 0, 0), (2, 0, text_rect.width + 12, text_rect.height + 8))
    drawrect(surface, (0, 0, 0), (0, 2, text_rect.width + 16, text_rect.height + 4))
    drawrect(surface, (44, 8, 99), (2, 2, text_rect.width + 12, 2))
    drawrect(surface, (44, 8, 99), (2, 4 + text_rect.height, text_rect.width + 12, 2))
    drawrect(surface, (44, 8, 99), (2, 2, 2, text_rect.height + 4))
    drawrect(surface, (44, 8, 99), (12 + text_rect.width, 2, 2, text_rect.height + 4))

    # Blitting the text onto the surface and returning it and the pos
    surface.blit(text, (8, 4))
    return surface, blit_pos

def block_collide(playerx: int, playery: int, width: float, height: float, detecting: list, block) -> tuple[bool, str]:
    """Checks collision between the player and the given block object.

    Args:
        playerx (int): The x position of the player.
        playery (int): The y position of the player.
        width (float): The width of the player.
        height (float): The height of the player.
        detecting (list): The detecting_rects lists used by the player (player.detecting_rects)
        block (Block, type not specified due to circular imports): The block object to check collision with.

    Returns:
        bool: True if the player is colliding with the block else False
        list: The detetcing_rects list with the new rect appended to it
    """

    player_rect = Rect(playerx, playery, width, height) # Rect that represents the player
    block_rect = Rect(block.pos.x, block.pos.y, BLOCK_SIZE, BLOCK_SIZE) # Rect that represents the block
    if not block.rect in detecting:
        detecting.append(block) # Adding the block rect to player.detecting_rects
    if player_rect.colliderect(block_rect): # Checking if the player is colliding with the block
        return True, detecting
    return False, detecting

def canter_pairing(tup: tuple) -> int:
    """Uses the Canter Pairing function to get a unique integer from a unique interger pair"""
    # Deal with negative numbers by turning positives into positive evens and negatives into positive odds
    a = 2 * tup[0] if tup[0] >= 0 else -2 * tup[0] - 1
    b = 2 * tup[1] if tup[1] >= 0 else -2 * tup[1] - 1
    return (a + b) * (a + b + 1) + b

def ascii_str_sum(string: str) -> int:
    """Gets the sum of the ASCII values of all the letters in a string"""
    return sum([ord(letter) for letter in string])

def rand_bool(perc: float) -> bool:
    """Returns True of False with the probability of the percentage given"""
    return random() < perc

def sign(num: int | float) -> int:
    return (num > 0) - (num < 0)

do_profile = False
def profile(callable: type, *args: tuple) -> Any:
    """Profiles the given callable and saves + prints the results

    Args:
        callable (type): A callabale type (function, constructor, ect)

    Returns:
        [...]: The result of calling the callable
    """

    global do_profile
    if do_profile: # Profile_bool stops the user from being able to hold down the profile key
        do_profile = False
        with cProfile.Profile() as profile: # Profiling the contents of the with block
            returnval = callable(*args)     # Calling the callable with the args

        # Naming the profile file in the format "profile_{hour}-{minute}-{second}.prof"
        statfile = Path(os.path.join(PROFILE_DIR, str(datetime.datetime.now().strftime("profile_%H-%M-%S")) + ".prof"))
        if not (statfile_dirpath := statfile.parent).exists():
            statfile_dirpath.mkdir() # Creating the dirpath of the statfile (ex. "build/profiles") if they do not exist
        stats = pstats.Stats(profile).sort_stats(pstats.SortKey.TIME) # Sorting the stats from highest time to lowest
        stats.dump_stats(filename=str(statfile)) # Saving the stats to a profile file
        stats.print_stats()                      # Printing the stats
        print(f"\n\n Profile saved to: {str(statfile)}!\n\n")
        return returnval
    else: # Return the output of the callable
        return callable(*args)