from block import Block

class Chunk(object):
    def __init__(self, pos):
        self.pos = pos
        self.block_data = generate_chunk(pos[0], pos[1])
        chunks[self.pos] = self

    def render(self):
        if self.pos in rendered_chunks:
            for block in self.block_data:
                if not block in blocks:
                    blocks[block] = Block(self, block, self.block_data[block])
                blocks[block].draw(screen)

    def debug(self):
        pygame.draw.rect(screen, (255, 255, 0), (self.pos[0]*CHUNK_SIZE*BLOCK_SIZE-player.camera.pos[0], self.pos[1]*CHUNK_SIZE*BLOCK_SIZE-player.camera.pos[1], CHUNK_SIZE*BLOCK_SIZE, CHUNK_SIZE*BLOCK_SIZE), width=1)