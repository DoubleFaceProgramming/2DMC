from random import randint
import metaball
import time

trials = int(1e6) # 1 million

print(f"Preparing {trials} random seeds...")
rand = [randint(0, int(1e6)) for _ in range(trials)]

print(f"Generating {trials} blobs...")
start = time.time()
for i in range(trials):
    metaball.blob(rand[i], 16, (3, 5), (4, 11), (2, 4))
print()
print(f"AVERAGE: {((time.time() - start) / trials):.8f}")
print(f"TOTAL: {(time.time() - start):.8f}")

# grid = [["." for _ in range(16)] for _ in range(16)]
# for pos in metaball.blob(randint(0, int(1e6)), 16, (3, 5), (4, 11), (2, 4)):
#     grid[pos[1]][pos[0]] = "#"
# for row in grid:
#     for ch in row:
#         print(ch, end=" ")
#     print()

# 0.0000057
# 0.0000022