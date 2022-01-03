import pygame
from pygame.locals import *
from random import *
from math import *
import json
import os
import opensimplex

FPS = 60
WIDTH, HEIGHT = 600, 300
SCR_DIM = (WIDTH, HEIGHT)
GRAVITY = 0.25
SLIDE = 0.15
TERMINAL_VEL = 12
BLOCK_SIZE = 32
CHUNK_SIZE = 8
SEED = randint(-2147483648, 2147483647)

def loading():
    font = pygame.font.SysFont('Comic Sans MS', 60)
    textsurface = font.render('Generating World...', True, (255, 255, 255))
    screen.blit(textsurface, (25, 100))
    display.blit(pygame.transform.scale(screen, (WIDTH*2, HEIGHT*2)), (0, 0))
    pygame.display.flip()

pygame.init()
display = pygame.display.set_mode((WIDTH*2, HEIGHT*2), HWSURFACE | DOUBLEBUF)
pygame.display.set_caption("2D Minecraft")
screen = pygame.Surface(SCR_DIM)
loading()
clock = pygame.time.Clock()
mixer = pygame.mixer.init()
vec = pygame.math.Vector2
noise = opensimplex.OpenSimplex(seed=SEED)
seed(SEED)

font12 = pygame.font.SysFont("consolas", 12)

block_textures = {}
for img in os.listdir("res/textures/blocks/"):
    block_textures[img[:-4]] = pygame.image.load("res/textures/blocks/"+img).convert_alpha()
for image in block_textures:
    block_textures[image] = pygame.transform.scale(block_textures[image], (BLOCK_SIZE, BLOCK_SIZE))
block_data = {}
for j in os.listdir("res/block_data/"):
    block_data[j[:-5]] = json.loads(open("res/block_data/"+j, "r").read())

player_head_img = pygame.image.load("res/textures/player/head.png").convert_alpha()
player_body_img = pygame.image.load("res/textures/player/body.png").convert_alpha()
player_arm_img = pygame.image.load("res/textures/player/arm.png").convert_alpha()
player_leg_img = pygame.image.load("res/textures/player/leg.png").convert_alpha()
head_size = vec(player_head_img.get_width()*2, player_head_img.get_height()*2)
body_size = vec(player_body_img.get_width()*2, player_body_img.get_height()*2)
arm_size = vec(player_arm_img.get_width()*2, player_arm_img.get_height()*2)
leg_size = vec(player_leg_img.get_width()*2, player_leg_img.get_height()*2)
player_head = pygame.Surface(head_size, SRCALPHA)
player_body = pygame.Surface(body_size, SRCALPHA)
player_arm = pygame.Surface(arm_size, SRCALPHA)
player_leg = pygame.Surface(leg_size, SRCALPHA)
player_head.blit(player_head_img, (head_size/4))
player_body.blit(player_body_img, (body_size/4))
player_arm.blit(player_arm_img, (arm_size/2+vec(-2, -2)))
player_leg.blit(player_leg_img, (leg_size/2+vec(-2, 0)))

def intv(vector):
    return vec(int(vector.x), int(vector.y))

def inttup(tup):
    return (int(tup[0]), int(tup[1]))

def text(text, color=(0, 0, 0)):
    return font12.render(text, True, color)

detecting_rects = []
def block_collide(ax, ay, width, height, b):
    a_rect = pygame.Rect(ax-camera.offset.x, ay-camera.offset.y, width, height)
    b_rect = pygame.Rect(b.pos.x-camera.offset.x, b.pos.y-camera.offset.y, BLOCK_SIZE, BLOCK_SIZE)
    detecting_rects.append(b_rect)
    if a_rect.colliderect(b_rect):
        return True
    return False

def remove_block(pos):
    pos = inttup(pos)
    chunk = (pos[0] // CHUNK_SIZE, pos[1] // CHUNK_SIZE)
    try:
        del blocks[pos]
        del chunks[chunk].block_data[pos]
    except:
        pass

def set_block(pos, name):
    pos = inttup(pos)
    chunk = (pos[0] // CHUNK_SIZE, pos[1] // CHUNK_SIZE)
    try:
        blocks[pos] = Block(chunks[chunk], pos, name)
        chunks[chunk].block_data[pos] = name
    except:
        pass

def is_occupied(pos):
    pos = inttup(pos)
    try: blocks[pos]
    except:
        if pygame.Rect(vec(pos)*BLOCK_SIZE, (BLOCK_SIZE, BLOCK_SIZE)).colliderect(pygame.Rect(player.pos, player.size)):
            return True
        return False
    else:
        try: blocks[pos].data["replaceable"]
        except: return True
        else: return False
    return True

def is_supported(pos, data, neighbors):
    if data["support"]:
        supports = data["support"]
        for support in supports:
            try: blocks[neighbors[support]]
            except: return False
            else:
                if blocks[neighbors[support]].name == supports[support]:
                    return True
        return False
    return True

def is_placable(pos, data, neighbors):
    if not is_occupied(pos) and is_supported(pos, data, neighbors):
        return True
    return False

class Camera(pygame.sprite.Sprite):
    def __init__(self, master):
        self.master = master
        self.actual_offset = self.master.size / 2
        self.actual_offset = self.master.pos - self.actual_offset - vec(SCR_DIM) / 2 + self.master.size / 2
        self.offset = intv(self.actual_offset)

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
        self.image = pygame.Surface((0.225*BLOCK_SIZE, 1.8*BLOCK_SIZE))
        self.image.fill((30, 30, 30))
        self.size = vec(0.225*BLOCK_SIZE, 1.8*BLOCK_SIZE)
        self.width, self.height = self.size.x, self.size.y
        self.start_pos = vec(0, 3) * BLOCK_SIZE # Far lands: 9007199254740993
        self.pos = vec(self.start_pos)
        self.coords = self.pos // BLOCK_SIZE
        self.vel = vec(0, 0)
        self.max_speed = 2.6
        self.jumping_max_speed = 3.3
        self.rect = pygame.Rect((0, 0, 0.225*BLOCK_SIZE, 1.8*BLOCK_SIZE))
        self.bottom_bar = pygame.Rect((self.rect.x+1, self.rect.bottom), (self.width-2, 1))
        self.on_ground = False
        self.holding = "grass_block"

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
            self.vel.y = -4.6
            self.vel.x *= 1.1
            if self.vel.x > self.jumping_max_speed:
                self.vel.x = self.jumping_max_speed
            elif self.vel.x < -self.jumping_max_speed:
                self.vel.x = -self.jumping_max_speed
        if -SLIDE < self.vel.x < SLIDE:
            self.vel.x = 0

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
        self.coords = self.pos // BLOCK_SIZE
        self.chunk = self.coords // CHUNK_SIZE
        self.rect.topleft = self.pos - camera.offset

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def move(self):
        for y in range(4):
            for x in range(3):
                try:
                    block = blocks[(int(self.coords.x-1+x), int(self.coords.y-1+y))]
                except:
                    pass
                else:
                    if block.data["collision_box"] == "full":
                        if self.vel.y < 0:
                            if block_collide(floor(self.pos.x), floor(self.pos.y+self.vel.y), self.width, self.height, block):
                                self.pos.y = floor(block.pos.y + BLOCK_SIZE)
                                self.vel.y = 0
                        elif self.vel.y >= 0:
                            if self.vel.x <= 0:
                                if block_collide(floor(self.pos.x), ceil(self.pos.y+self.vel.y), self.width, self.height, block):
                                    self.pos.y = ceil(block.pos.y - self.height)
                                    self.vel.y = 0
                            elif self.vel.x > 0:
                                if block_collide(ceil(self.pos.x), ceil(self.pos.y+self.vel.y), self.width, self.height, block):
                                    self.pos.y = ceil(block.pos.y - self.height)
                                    self.vel.y = 0
                        if self.vel.x < 0:
                            if block_collide(floor(self.pos.x+self.vel.x), floor(self.pos.y), self.width, self.height, block):
                                self.pos.x = floor(block.pos.x + BLOCK_SIZE)
                                self.vel.x = 0
                        elif self.vel.x >= 0:
                            if block_collide(ceil(self.pos.x+self.vel.x), ceil(self.pos.y), self.width, self.height, block):
                                self.pos.x = ceil(block.pos.x - self.width)
                                self.vel.x = 0
        self.pos += self.vel

class Block(pygame.sprite.Sprite):
    def __init__(self, chunk, pos, name):
        pygame.sprite.Sprite.__init__(self)
        blocks[tuple(pos)] = self
        self.name = name
        self.data = block_data[self.name]
        self.chunk = chunk
        self.coords = vec(pos)
        self.pos = self.coords * BLOCK_SIZE
        self.neighbors = {
            "up": inttup((self.coords.x, self.coords.y-1)), 
            "down": inttup((self.coords.x, self.coords.y+1)), 
            "left": inttup((self.coords.x-1, self.coords.y)), 
            "right": inttup((self.coords.x+1, self.coords.y))
        }
        self.image = block_textures[self.name]
        if self.data["collision_box"] == "full":
            self.rect = pygame.Rect(self.pos, (BLOCK_SIZE, BLOCK_SIZE))
        elif self.data["collision_box"] == "none":
            self.rect = pygame.Rect(self.pos, (0, 0))

    def update(self):
        if not is_supported(self.pos, self.data, self.neighbors):
            remove_blocks.append(self.coords)
        self.rect.topleft = self.pos - camera.offset

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

class Chunk(object):
    def __init__(self, pos):
        self.pos = pos
        self.block_data = generate_chunk(pos[0], pos[1])
        for block in self.block_data:
            blocks[block] = Block(self, block, self.block_data[block])

    def render(self):
        if self.pos in rendered_chunks:
            for block in self.block_data:
                try: blocks[block]
                except:
                    blocks[block] = Block(self, block, self.block_data[block])
                blocks[block].update()
                blocks[block].draw(screen)

    def debug(self):
        pygame.draw.rect(screen, (255, 255, 0), (self.pos[0]*CHUNK_SIZE*BLOCK_SIZE-camera.offset[0], self.pos[1]*CHUNK_SIZE*BLOCK_SIZE-camera.offset[1], CHUNK_SIZE*BLOCK_SIZE, CHUNK_SIZE*BLOCK_SIZE), width=1)

def generate_chunk(x, y):
    chunk_data = {}
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target = (x * CHUNK_SIZE + x_pos, y * CHUNK_SIZE + y_pos)
            block_name = ""
            height = int(noise.noise2d(target[0]*0.1, 0)*5)
            if target[1] == 5-height:
                block_name = "grass_block"
            elif 5-height < target[1] < 10-height:
                block_name = "dirt"
            elif target[1] >= 10-height:
                block_name = "stone"
            elif target[1] == 4-height:
                if randint(0, 2) == 0:
                    block_name = "grass"
            if block_name != "":
                chunk_data[target] = block_name
    return chunk_data

blocks = {}
chunks = {}
player = Player()
camera = Camera(player)

remove_blocks = []

def draw():
    screen.fill((135, 206, 250))
    for chunk in rendered_chunks:
        chunks[chunk].render()
    player.draw(screen)
    screen.blit(text(f"Holding: {player.holding}", color=(255, 255, 255)), (0, HEIGHT-12))
    if debug:
        for chunk in rendered_chunks:
            chunks[chunk].debug()
        pygame.draw.rect(screen, (255, 255, 255), player.rect, width=1)
        for rect in detecting_rects:
            pygame.draw.rect(screen, (255, 0, 0), rect, width=1)
        detecting_rects.clear()
        screen.blit(text(f"Seed: {SEED}"), (0, 0))
        screen.blit(text(f"Velocity: {(round(player.vel.x, 3), round(player.vel.y, 3))}"), (0, 12))
        screen.blit(text(f"Position: {inttup(player.coords)}"), (0, 24))
        screen.blit(text(f"Camera offset: {inttup(player.pos-camera.offset-vec(SCR_DIM)/2+player.size/2)}"), (0, 36))
        mpos = vec(pygame.mouse.get_pos())
        block_pos = (player.pos+(mpos/2-player.rect.topleft))//BLOCK_SIZE
        screen.blit(text(f"Chunk: {inttup(player.coords//CHUNK_SIZE)}"), (0, 48))
        screen.blit(text(f"Chunks loaded: {len(chunks)}"), (0, 60))
        screen.blit(text(f"Rendered blocks: {len(blocks)}"), (0, 72))
        try:
            screen.blit(text(f"{blocks[inttup(block_pos)].name.replace('_', ' ')}", color=(255, 255, 255)), (mpos[0]/2, mpos[1]/2-12))
        except:
            pass
    display.blit(pygame.transform.scale(screen, (WIDTH*2, HEIGHT*2)), (0, 0))
    pygame.display.flip()

running = True
debug = False

while running:
    dt = clock.tick(FPS) / 16
    pygame.display.set_caption(f"2D Minecraft | FPS: {int(clock.get_fps())}")

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == MOUSEBUTTONDOWN:
            mpos = vec(pygame.mouse.get_pos())
            block_pos = (player.pos+(mpos/2-player.rect.topleft))//BLOCK_SIZE
            if event.button == 1:
                remove_block(block_pos)
            if event.button == 3:
                if not is_occupied(block_pos):
                    set_block(block_pos, player.holding)
                    blocks[inttup(block_pos)].update()
        if event.type == KEYDOWN:
            if event.key == K_1:
                player.holding = "grass_block"
            elif event.key == K_2:
                player.holding = "dirt"
            elif event.key == K_3:
                player.holding = "stone"
            elif event.key == K_4:
                player.holding = "grass"
            if event.key == K_F5:
                debug = not debug

    rendered_chunks = []
    for y in range(int(HEIGHT/(CHUNK_SIZE*BLOCK_SIZE)+2)):
        for x in range(int(WIDTH/(CHUNK_SIZE*BLOCK_SIZE)+2)):
            chunk = (
                x - 1 + int(round(camera.offset.x / (CHUNK_SIZE * BLOCK_SIZE))), 
                y - 1 + int(round(camera.offset.y / (CHUNK_SIZE * BLOCK_SIZE)))
            )
            rendered_chunks.append(chunk)
            if chunk not in chunks:
                chunks[chunk] = Chunk(chunk)
    unrendered_chunks = []
    for y in range(int(HEIGHT/(CHUNK_SIZE*BLOCK_SIZE)+4)):
        for x in range(int(WIDTH/(CHUNK_SIZE*BLOCK_SIZE)+4)):
            chunk = (
                x - 2 + int(round(camera.offset.x / (CHUNK_SIZE * BLOCK_SIZE))), 
                y - 2 + int(round(camera.offset.y / (CHUNK_SIZE * BLOCK_SIZE)))
            )
            try: chunks[chunk]
            except: pass
            else:
                if chunk not in rendered_chunks:
                    unrendered_chunks.append(chunk)
    for chunk in unrendered_chunks:
        for block in chunks[chunk].block_data:
            if block in blocks:
                blocks[block].kill()
                del blocks[block]
    for block in remove_blocks:
        remove_block(block)
    remove_blocks = []

    camera.update()
    player.update()
    draw()

pygame.quit()
quit()
