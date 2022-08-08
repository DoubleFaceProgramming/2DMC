from fishhook import hook

@hook(list)
def reverse_nip(self):
    rev = self.copy()
    rev.reverse()
    return rev

class Block:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, o) -> bool:
        return self.name == o.name

blocks1 = [Block("stone"), Block("dirt"), Block("glass")]
blocks2 = [Block("dandelion"), Block("dirt"), Block("bobirty")]
blocks3 = [Block("stone"), Block("poppy"), Block("grass")]
blocks4 = [Block("glass"), Block("glass"), Block("poppy")]
blocks5 = [Block("poppy"), Block("poppy"), Block("stone")]

def highest_opaque_block(blocks):
    rev = blocks.reverse_nip()
    for index, block in enumerate(rev):
        if not block: continue
        if block.name not in {"glass", "tall_grass", "tall_grass_top", "grass", "dandelion", "poppy"}: # <- tags go here
            return rev[:index + 1].reverse_nip()

    return blocks

print(1, *highest_opaque_block(blocks1))
print(2, *highest_opaque_block(blocks2))
print(3, *highest_opaque_block(blocks3))
print(4, *highest_opaque_block(blocks4))
print(5, *highest_opaque_block(blocks5))

assert highest_opaque_block(blocks1) == [Block("dirt"), Block("glass")]
assert highest_opaque_block(blocks2) == [Block("bobirty")]
assert highest_opaque_block(blocks3) == [Block("stone"), Block("poppy"), Block("grass")]
assert highest_opaque_block(blocks4) == [Block("glass"), Block("glass"), Block("poppy")]
assert highest_opaque_block(blocks5) == [Block("stone")]