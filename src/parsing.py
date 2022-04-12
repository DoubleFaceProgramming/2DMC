# 2DMC is a passion project to recreate the game "Minecraft" (all credit to Mojang Studios) in 2D.
# Copyright (C) 2022 Doubleface
# You can view the terms of the GPL License in LICENSE.md

# The majority of the game assets are properties of Mojang Studios,
# you can view their TOS here: https://account.mojang.com/documents/minecraft_eula

from pathlib import Path
from os.path import join
from os import listdir
import json

from build.exe_comp import pathof

def load_block_data() -> dict:
    # Load json block data into a dictionary
    block_data = {}
    for file in listdir(pathof("data/blocks/")):
        block_data[Path(file).stem] = json.loads(open(pathof(join("data/blocks/", file)), "r").read())

    return block_data

def load_ore_distribution() -> dict:
    ore_distribution = {}
    for file in listdir(pathof("data/ore_distribution/")):
        ore_distribution[Path(file).stem] = json.loads(open(pathof(join("data/ore_distribution/", file)), "r").read())
    
    return ore_distribution

def load_structures() -> dict:
    """Load the structure data files into a dictionary.

    Returns:
        dict: A dictionary containing structure information
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