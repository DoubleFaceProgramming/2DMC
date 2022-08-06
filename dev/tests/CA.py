from timer import timer
from random import randint
import numpy as np
from functools import cache

def CA_1(size: tuple, density: int, cycles: int) -> dict:
    is_empty = True
    while is_empty:
        blob = []

        for y in range(size[1]):
            blob.append([])
            for x in range(size[0]):
                if randint(0, 10) < density:
                    blob[y].append(" ")
                else:
                    blob[y].append("#")

        neighbors_offset = [(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]

        for _ in range(cycles):
            for y, line in enumerate(blob):
                for x, block in enumerate(line):
                    neighbors = 0
                    for n in neighbors_offset:
                        try:
                            if blob[y+n[0]][x+n[1]] == "#":
                                neighbors += 1
                        except: pass
                    if neighbors <= 3:
                        blob[y][x] = " "
                    elif neighbors > 5:
                        blob[y][x] = "#"

        blob_dict = {}
        for y, line in enumerate(blob):
            for x, block in enumerate(line):
                if block != " ":
                    is_empty = False
                    blob_dict[(x, y)] = block

    return blob_dict

@cache
def CA_2(size: tuple, density: int, cycles: int) -> dict:
    is_empty = True
    while is_empty:
        blob = np.empty((size[1], size[0]))

        for y in range(size[1]):
            for x in range(size[0]):
                blob[y, x] = not (randint(0, 10) < density)

        neighbors_offset = [(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]

        for _ in range(cycles):
            for y, line in enumerate(blob):
                for x, block in enumerate(line):
                    neighbors = 0
                    for n in neighbors_offset:
                        try:
                            if blob[y+n[0],x+n[1]]:
                                neighbors += 1
                        except: pass
                    if neighbors <= 3:
                        blob[y,x] = False
                    elif neighbors > 5:
                        blob[y,x] = True

        blob_dict = {}
        for y, line in enumerate(blob):
            for x, block in enumerate(line):
                if block:
                    is_empty = False
                    blob_dict[(x, y)] = block

    return blob_dict

trials = 500
avg = 0
for _ in range(trials):
    avg += timer(CA_1, (10, 10), 5, 3)
avg /= trials
print(f"CA_1 average time: {avg}; {trials} trials")

avg = 0
for _ in range(trials):
    avg += timer(CA_2, (10, 10), 5, 3)
avg /= trials
print(f"CA_2 average time: {avg}; {trials} trials")