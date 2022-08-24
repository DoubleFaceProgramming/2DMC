from random import randint
import metaball
import time

trials = 100000

start = time.time()
for _ in range(trials):
    metaball.blob(100000)
print(f"{((time.time() - start) / trials):.20f}")

# grid = [["." for _ in range(16)] for _ in range(16)]
# for pos in metaball.blob(randint(0, 10000000)):
#     grid[pos[1]][pos[0]] = "#"
# for row in grid:
#     for ch in row:
#         print(ch, end=" ")
#     print()

# 0.00000477