import pygame
from pygame.locals import *
from random import *
from math import *
import perlin
import json
import os

FPS = 60
WIDTH, HEIGHT = 600, 300
SCR_DIM = (WIDTH, HEIGHT)
GRAVITY = 0.25
SLIDE = 0.15
TERMINAL_VEL = 18
BLOCK_SIZE = 32
CHUNK_SIZE = 8
BLOCK_TEXTURES_DIR = "res/textures/blocks/"
BLOCK_DATA_DIR = "res/block_data/"

pygame.init()
display = pygame.display.set_mode((WIDTH*2, HEIGHT*2), HWSURFACE | DOUBLEBUF)
screen = pygame.Surface(SCR_DIM)
clock = pygame.time.Clock()
mixer = pygame.mixer.init()
vec = pygame.math.Vector2
noise = perlin.Perlin(randint(0, 1000000))

font = pygame.font.SysFont('Comic Sans MS', 100)
textsurface = font.render('Generating World...', True, (255, 255, 255))
screen.blit(textsurface, (50, 200))
pygame.display.flip()

block_textures = {}
for img in os.listdir(BLOCK_TEXTURES_DIR):
    block_textures[img[:-4]] = pygame.image.load(BLOCK_TEXTURES_DIR+img).convert_alpha()
for image in block_textures:
    block_textures[image] = pygame.transform.scale(block_textures[image], (BLOCK_SIZE, BLOCK_SIZE))
block_data = {}
for j in os.listdir(BLOCK_DATA_DIR):
    block_data[j[:-5]] = json.loads(open(BLOCK_DATA_DIR+j, "r").read())

def intv(vector):
    return vec(int(vector.x), int(vector.y))

def block_collide(ax, ay, width, height, b):
    a_rect = pygame.Rect(ax-camera.offset.x, ay-camera.offset.y, width, height)
    b_rect = pygame.Rect(b.pos.x-camera.offset.x, b.pos.y-camera.offset.y, BLOCK_SIZE, BLOCK_SIZE)
    if a_rect.colliderect(b_rect):
        return True
    return False

class Camera(pygame.sprite.Sprite):
    def __init__(self, master):
        self.master = master
        self.actual_offset = self.master.size / 2
        self.offset = intv(self.actual_offset)
        self.actual_offset = self.master.pos - self.offset - vec(SCR_DIM) / 2 + self.master.size / 2

    def update(self):
        tick_offset = self.master.pos - self.offset - vec(SCR_DIM) / 2 + self.master.size / 2
        if -1 < tick_offset.x < 1:
            tick_offset.x = 0
        if -1 < tick_offset.y < 1:
            tick_offset.y = 0
        self.actual_offset += tick_offset / 10
        self.offset = intv(self.actual_offset)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((0.6*BLOCK_SIZE, 1.8*BLOCK_SIZE))
        self.size = vec(self.image.get_size())
        self.width, self.height = self.size.x, self.size.y
        self.image.fill((40, 40, 40))
        self.start_pos = vec(0, 0) * BLOCK_SIZE
        self.pos = vec(self.start_pos)
        self.vel = vec(0, 0)
        self.max_speed = 2.6
        self.jumping_max_speed = 3.2
        self.rect = self.image.get_rect()
        self.bottom_bar = pygame.Rect((self.rect.x+1, self.rect.bottom), (self.width-2, 1))
        self.on_ground = False

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_a]:
            if self.vel.x > -self.max_speed:
                self.vel.x -= SLIDE
        elif self.vel.x < 0:
            self.vel.x += SLIDE
        if keys[K_d]:
            if self.vel.x < self.max_speed:
                self.vel.x += SLIDE
        elif self.vel.x > 0:
            self.vel.x -= SLIDE
        if keys[K_w] and self.on_ground:
            self.vel.y = -4.5
            self.vel.x *= 1.1
            if self.vel.x > self.jumping_max_speed:
                self.vel.x = self.jumping_max_speed
            elif self.vel.x < -self.jumping_max_speed:
                self.vel.x = -self.jumping_max_speed
        if -SLIDE < self.vel.x < SLIDE:
            self.vel.x = 0

        if not self.on_ground:
            self.vel.y += GRAVITY
        if self.vel.y > TERMINAL_VEL:
            self.vel.y = TERMINAL_VEL
        self.move()
        self.bottom_bar = pygame.Rect((self.rect.left+1, self.rect.bottom), (self.width-2, 1))
        for block in blocks:
            if self.bottom_bar.colliderect(blocks[block].rect):
                self.on_ground = True
                break
        else:
            self.on_ground = False
        self.rect.topleft = self.pos - camera.offset

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def move(self):
        for b in blocks:
            block = blocks[b]
            if block.data["collision_box"] == "full":
                if block_collide(self.pos.x+self.vel.x, self.pos.y, self.width, self.height, block):
                    if self.vel.x < 0:
                        self.pos.x -= self.pos.x - (block.pos.x + BLOCK_SIZE)
                    elif self.vel.x >= 0:
                        self.pos.x += block.pos.x - (self.pos.x + self.width)
                    self.vel.x = 0
                if block_collide(self.pos.x, self.pos.y+self.vel.y, self.width, self.height, block):
                    if self.vel.y < 0:
                        self.pos.y -= self.pos.y - (block.pos.y + BLOCK_SIZE)
                    elif self.vel.y >= 0:
                        self.pos.y += block.pos.y - (self.pos.y + self.height)
                    self.vel.y = 0
        self.pos += self.vel

class Block(pygame.sprite.Sprite):
    def __init__(self, pos, name):
        pygame.sprite.Sprite.__init__(self)
        blocks[tuple(pos)] = self
        self.name = name
        self.data = block_data[self.name]
        self.pos = vec(pos) * BLOCK_SIZE
        self.image = block_textures[self.name]
        if self.data["collision_box"] == "full":
            self.rect = pygame.Rect(self.pos, (BLOCK_SIZE, BLOCK_SIZE))
        elif self.data["collision_box"] == "none":
            self.rect = pygame.Rect(self.pos, (0, 0))

    def update(self):
        self.rect.topleft = self.pos - camera.offset

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

class Chunk(object):
    def __init__(self, pos):
        self.block_data = generate_chunk(pos[0], pos[1])
        self.blocks = {}
        for block in self.block_data:
            self.blocks[block] = Block(block, self.block_data[block])

    def render(self):
        for block in self.blocks:
            for chunk in rendered_chunks:
                if block in chunks[chunk].block_data:
                    self.blocks[block] = Block(block, chunks[chunk].block_data[block])
            self.blocks[block].update()
            self.blocks[block].draw(screen)

def generate_chunk(x, y):
    chunk_data = {}
    chunk_data_pos_only = {}
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + x_pos
            target_y = y * CHUNK_SIZE + y_pos
            block_name = ""
            height = int(noise.one(target_x * 0.8))
            if target_y == 5-height:
                block_name = "grass_block"
            elif 5-height < target_y < 10-height:
                block_name = "dirt"
            elif target_y >= 10-height:
                block_name = "stone"
            elif target_y == 4-height:
                if randint(0, 2) == 0:
                    block_name = "grass"
            if block_name != "":
                chunk_data[(target_x, target_y)] = block_name
    return chunk_data

blocks = {}
chunks = {}
player = Player()
camera = Camera(player)

def draw():
    screen.fill((135, 206, 250))
    for chunk in rendered_chunks:
        chunks[chunk].render()
    player.draw(screen)
    display.blit(pygame.transform.scale(screen, (WIDTH*2, HEIGHT*2)), (0, 0))
    pygame.display.flip()

running = True
while running:
    clock.tick(FPS)
    try:
        pygame.display.set_caption(f"FPS: {round(clock.get_fps(), 1)} #blocks: {len(blocks)} #chunks: {len(chunks)}")
    except:
        pass

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    rendered_chunks = {}
    for y in range(ceil(HEIGHT/(CHUNK_SIZE*BLOCK_SIZE)+1)):
        for x in range(ceil(WIDTH/(CHUNK_SIZE*BLOCK_SIZE)+1)):
            chunk = (
                x - 1 + int(round(camera.offset.x / (CHUNK_SIZE * BLOCK_SIZE))), 
                y - 1 + int(round(camera.offset.y / (CHUNK_SIZE * BLOCK_SIZE)))
            )
            rendered_chunks[chunk] = None
            if chunk not in chunks:
                chunks[chunk] = Chunk(chunk)
    unrendered_chunks = {}
    for chunk in chunks:
        if chunk not in rendered_chunks:
            unrendered_chunks[chunk] = None
    for chunk in unrendered_chunks:
        for block in chunks[chunk].block_data:
            if block in blocks:
                blocks[block].kill()
                del blocks[block]

    camera.update()
    player.update()
    draw()

pygame.quit()
quit()
