from dataclasses import dataclass
from random import randint
from math import dist
import time

from my_profile import profile

@dataclass
class Metaball:
    center: tuple[int, int]
    radius: float

def blob(ball_size, ball_num):
    balls = [Metaball((randint(4, 11), randint(4, 11)), ball_size) for _ in range(ball_num)]

    result = []

    for y in range(16):
        result.append([])
        for x in range(16):
            if sum([(ball.radius / distance / 2) if (distance := dist(ball.center, (x, y))) else 10 for ball in balls]) > 1.2:
                result[y].append("#")
            else:
                result[y].append(".")

    return result

    # return [["#" if sum([(ball.radius / distance / 2) if (distance := dist(ball.center, (x, y))) else 10 for ball in balls]) > 1.2 else "." for x in range(16)] for y in range(16)]

# Generate 1 blob
# blob_list = blob(randint(2, 4), randint(3, 4))

# Profile 1 blob
# blob_list = profile(blob, randint(2, 4), randint(3, 4))

# Average time
start = time.time()
for _ in range(100000):
    blob_list = blob(randint(2, 4), randint(3, 4))
print((time.time() - start) / 100000)

# Write to file
# final = ""
# for _ in range(100):
#     blob_list = blob(randint(2, 4), randint(3, 4))
#     for row in blob_list:
#         final += " ".join(row) + "\n"
#     final += "\n\n\n"
# with open("blobs.txt", "w") as f:
#     f.write(final)

# Print 1 blob
# for row in blob_list:
#     for ch in row:
#         print(ch, end=" ")
#     print()