from random import randint, seed, choices, randrange
from math import cos, ceil, floor
import json
import os
import opensimplex
from perlin_noise import PerlinNoise
import time
import win32api
import pygame
from pygame.locals import  (
    HWSURFACE, SRCALPHA, DOUBLEBUF,
    K_w, K_e, K_a, K_d,
    K_1, K_9, K_0, K_F5,
    MOUSEBUTTONDOWN, KEYDOWN,
    QUIT,
)

WIDTH, HEIGHT = 1200, 600
SCR_DIM = (WIDTH, HEIGHT)
GRAVITY = 0.5
SLIDE = 0.3
TERMINAL_VEL = 24
BLOCK_SIZE = 64
CHUNK_SIZE = 8
SEED = randint(-2147483648, 2147483647)

settings = win32api.EnumDisplaySettings(win32api.EnumDisplayDevices().DeviceName, -1)
monitor_refresh_rate = getattr(settings, "DisplayFrequency")
FPS = monitor_refresh_rate
REGULAR_FONT_LOC = "assets/fonts/regular.ttf"

def loading():
    font = pygame.font.Font(REGULAR_FONT_LOC, 120)
    textsurface = font.render("Generating World...", True, (255, 255, 255))
    screen.blit(textsurface, (50, 200))
    pygame.display.flip()

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE | DOUBLEBUF)
pygame.display.set_caption("2D Minecraft")
loading()
clock = pygame.time.Clock()
mixer = pygame.mixer.init()
vec = pygame.math.Vector2
noise = opensimplex.OpenSimplex(seed=SEED)
pnoise = PerlinNoise(seed=SEED)
seed(SEED)

font24 = pygame.font.Font(REGULAR_FONT_LOC, 24)
font20 = pygame.font.Font(REGULAR_FONT_LOC, 20)

block_textures = {}
for img in os.listdir("assets/textures/blocks/"):
    block_textures[img[:-4]] = pygame.image.load("assets/textures/blocks/"+img).convert()
for image in block_textures:
    block_textures[image] = pygame.transform.scale(block_textures[image], (BLOCK_SIZE, BLOCK_SIZE))
    block_textures[image].set_colorkey((255, 255, 255))
block_data = {}
for j in os.listdir("data/blocks/"):
    block_data[j[:-5]] = json.loads(open("data/blocks/"+j, "r").read())
structures = {}
for folder in os.listdir("data/structures/"):
    structures[folder] = {}
    for struct in os.listdir("data/structures/" + folder):
        if struct != "distribution.structure":
            data = open(f"data/structures/{folder}/{struct}", "r").readlines()
            split = data.index("structure:\n")
            split2 = data.index("origin:\n")
            legends = {legend.split(":")[0]: legend.split(":")[1] for legend in [legend[:-1] for legend in data[:split]]}
            structure = [line[:-1] for line in data[split+1:split2]]
            origin = (int(data[-1].split(" ")[0]), int(data[-1].split(" ")[1]))
            blocks = {}
            for y in range(len(structure)):
                for x in range(len(structure[y])):
                    try: legends[structure[y][x]]
                    except: pass
                    else: blocks[(x-origin[0], y-origin[1])] = legends[structure[y][x]]
            structures[folder][struct[:-10]] = (origin, blocks)
        else:
            distribution = open(f"data/structures/{folder}/distribution.structure", "r").readlines()
            weights = [int(d[:-2].split(" ")[1]) for d in distribution]
            files = [d[:-2].split(" ")[0] for d in distribution]
            structures[folder]["distribution"] = {"weights": weights, "files": files}

player_head_img = pygame.image.load("assets/textures/player/head.png").convert()
player_body_img = pygame.image.load("assets/textures/player/body.png").convert()
player_arm_img = pygame.image.load("assets/textures/player/arm.png").convert()
player_leg_img = pygame.image.load("assets/textures/player/leg.png").convert()
player_head_img = pygame.transform.scale(player_head_img, (28, 28))
player_body_img = pygame.transform.scale(player_body_img, (14, 43))
player_leg_img = pygame.transform.scale(player_leg_img, (14, 45))
player_arm_img = pygame.transform.scale(player_arm_img, (14, 43))
head_size = vec(player_head_img.get_width()*2, player_head_img.get_height()*2)
body_size = vec(player_body_img.get_width()*2, player_body_img.get_height()*2)
arm_size = vec(player_arm_img.get_width()*2, player_arm_img.get_height()*2)
leg_size = vec(player_leg_img.get_width()*2, player_leg_img.get_height()*2)
player_head = pygame.Surface(head_size, SRCALPHA)
player_body = pygame.Surface(body_size, SRCALPHA)
player_arm = pygame.Surface(arm_size, SRCALPHA)
player_leg = pygame.Surface(leg_size, SRCALPHA)
player_head.blit(player_head_img, (head_size/4+vec(0, -8)))
player_body.blit(player_body_img, (body_size/4))
player_arm.blit(player_arm_img, (arm_size/2+vec(-7, -6)))
player_leg.blit(player_leg_img, (leg_size/2+vec(-7, -2)))
invert_player_head = pygame.transform.flip(player_head, True, False)
invert_player_body = pygame.transform.flip(player_body, True, False)
invert_player_arm = pygame.transform.flip(player_arm, True, False)
invert_player_leg = pygame.transform.flip(player_leg, True, False)

inventory_img = pygame.image.load("assets/textures/gui/inventory.png").convert_alpha()
inventory_img = pygame.transform.scale(inventory_img, (int(inventory_img.get_width()*2.5), int(inventory_img.get_height()*2.5)))
hotbar_img = pygame.image.load("assets/textures/gui/hotbar.png").convert_alpha()
hotbar_img = pygame.transform.scale(hotbar_img, (int(hotbar_img.get_width()*2.5), int(hotbar_img.get_height()*2.5)))
hotbar_selection_img = pygame.image.load("assets/textures/gui/hotbar_selection.png").convert_alpha()
hotbar_selection_img = pygame.transform.scale(hotbar_selection_img, (int(hotbar_selection_img.get_width()*2.5), int(hotbar_selection_img.get_height()*2.5)))

def intv(vector):
    return vec(int(vector.x), int(vector.y))

def inttup(tup):
    return (int(tup[0]), int(tup[1]))

def in_dict(dict, key):
    try: dict[key]
    except: return False
    else: return True

def text(text, color=(0, 0, 0)):
    return font24.render(text, True, color)

def smol_text(text, color=(255, 255, 255)):
    return font20.render(text, True, color)

def blit_text_box(screen, text, pos, opacity):
    text_rect = text.get_rect()
    blit_pos = pos
    surface = pygame.Surface((text_rect.width+16, text_rect.height+8), SRCALPHA)
    surface.set_alpha(opacity)
    pygame.draw.rect(surface, (0, 0, 0), (2, 0, text_rect.width+12, text_rect.height+8))
    pygame.draw.rect(surface, (0, 0, 0), (0, 2, text_rect.width+16, text_rect.height+4))
    pygame.draw.rect(surface, (44, 8, 99), (2, 2, text_rect.width+12, 2))
    pygame.draw.rect(surface, (44, 8, 99), (2, 4+text_rect.height, text_rect.width+12, 2))
    pygame.draw.rect(surface, (44, 8, 99), (2, 2, 2, text_rect.height+4))
    pygame.draw.rect(surface, (44, 8, 99), (12+text_rect.width, 2, 2, text_rect.height+4))
    surface.blit(text, (8, 4))
    screen.blit(surface, blit_pos)

detecting_rects = []
def block_collide(ax, ay, width, height, b):
    a_rect = pygame.Rect(ax-camera.pos.x, ay-camera.pos.y, width, height)
    b_rect = pygame.Rect(b.pos.x-camera.pos.x, b.pos.y-camera.pos.y, BLOCK_SIZE, BLOCK_SIZE)
    detecting_rects.append(b_rect)
    if a_rect.colliderect(b_rect):
        return True
    return False

def remove_block(pos, data, neighbors):
    pos = inttup(pos)
    for _ in range(randint(18, 26)):
        Particle("block", vec(pos)*BLOCK_SIZE+vec(randint(0, BLOCK_SIZE), randint(0, BLOCK_SIZE)), master=blocks[pos])
    chunk = (pos[0] // CHUNK_SIZE, pos[1] // CHUNK_SIZE)
    if in_dict(data, "next_layer"):
        blocks[pos] = Block(chunk, pos, data["next_layer"])
        chunks[chunk].block_data[pos] = data["next_layer"]
    else:
        del blocks[pos]
        del chunks[chunk].block_data[pos]
    for neighbor in neighbors:
        if in_dict(blocks, neighbors[neighbor]):
            blocks[neighbors[neighbor]].update()

def set_block(pos, name, neighbors):
    pos = inttup(pos)
    chunk = (pos[0] // CHUNK_SIZE, pos[1] // CHUNK_SIZE)
    try:
        blocks[pos] = Block(chunks[chunk], pos, name)
        chunks[chunk].block_data[pos] = name
    except: pass
    for neighbor in neighbors:
        chunk = (neighbors[neighbor][0] // CHUNK_SIZE, neighbors[neighbor][1] // CHUNK_SIZE)
        if in_dict(blocks, neighbors[neighbor]):
            blocks[neighbors[neighbor]].update()

def is_occupied(pos):
    pos = inttup(pos)
    if not pygame.Rect(vec(pos)*BLOCK_SIZE, (BLOCK_SIZE, BLOCK_SIZE)).colliderect(pygame.Rect(player.pos, player.size)):
        if in_dict(blocks, pos):
            return not in_dict(blocks[pos].data, "replaceable")
        else:
            return False
    return True

def is_supported(pos, data, neighbors, c=False):
    if data["support"]:
        supports = data["support"]
        for support in supports:
            if inttup(support.split(" ")) != inttup(vec(c)-vec(pos)):
                if in_dict(blocks, neighbors[support]):
                    if blocks[neighbors[support]].name not in supports[support]:
                        return False
                else:
                    return False
            else:
                return True
    return True

def is_placeable(pos, data, neighbors, c=False):
    if not is_occupied(pos) and is_supported(pos, data, neighbors, c=c):
        return True
    return False

class Camera(pygame.sprite.Sprite):
    def __init__(self, master):
        self.master = master
        self.pos = self.master.size / 2
        self.pos = self.master.pos - self.pos - vec(SCR_DIM) / 2 + self.master.size / 2

    def update(self):
        mpos = pygame.mouse.get_pos()
        tick_offset = self.master.pos - self.pos - vec(SCR_DIM) / 2 + self.master.size / 2
        if -1 < tick_offset.x < 1:
            tick_offset.x = 0
        if -1 < tick_offset.y < 1:
            tick_offset.y = 0
        if not inventory.visible:
            x_dist, y_dist = mpos[0] - SCR_DIM[0] / 2, mpos[1] - SCR_DIM[1] / 2
        else:
            x_dist, y_dist = 0, 0
        dist_squared = vec(x_dist**2 if x_dist > 0 else -x_dist**2, y_dist**2*2.5 if y_dist > 0 else -y_dist**2*2.5)
        
        self.pos += (tick_offset / 10 + vec(dist_squared) / 18000) * dt

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = vec(0.225*BLOCK_SIZE, 1.8*BLOCK_SIZE)
        self.width, self.height = self.size.x, self.size.y
        self.start_pos = vec(0, 3) * BLOCK_SIZE # Far lands: 9007199254740993 (aka 2^53)
        self.pos = vec(self.start_pos)
        self.coords = self.pos // BLOCK_SIZE
        self.acc = vec(0, 0)
        self.vel = vec(0, 0)
        # Walking speed: 4.317 bps
        # Sprinting speed: 5.612 bps
        # Sprint-jumping speed: 7.127 bps
        self.max_speed = 5.153
        self.jumping_max_speed = 6.7
        self.rect = pygame.Rect((0, 0, 0.225*BLOCK_SIZE, 1.8*BLOCK_SIZE))
        self.bottom_bar = pygame.Rect((self.rect.x+1, self.rect.bottom), (self.width-2, 1))
        self.on_ground = False
        self.holding = "grass_block"
        self.direction = "right"
        
        self.head, self.body, self.leg, self.leg2, self.arm, self.arm2 = [pygame.sprite.Sprite() for _ in range(6)]
        self.head.image, self.body.image, self.leg.image = player_head, player_body, player_leg
        self.leg2.image, self.arm.image, self.arm2.image = player_leg, player_arm, player_arm
        self.head.rect, self.body.rect = self.head.image.get_rect(), self.body.image.get_rect()
        self.leg.rect, self.leg2.rect = self.leg.image.get_rect(), self.leg2.image.get_rect()
        self.arm.rect, self.arm2.rect = self.arm.image.get_rect(), self.arm2.image.get_rect()
        self.head.rot = 0
        self.leg.count = 0
        self.leg.rot = 0
        self.leg2.rot = 0
        self.arm.rot = 0
        self.arm2.rot = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_a] and not inventory.visible:
            if self.vel.x > -self.max_speed:
                self.vel.x -= SLIDE * dt
        elif self.vel.x < 0:
            self.vel.x += SLIDE * dt
        if keys[K_d] and not inventory.visible:
            if self.vel.x < self.max_speed:
                self.vel.x += SLIDE * dt
        elif self.vel.x > 0:
            self.vel.x -= SLIDE * dt
        if keys[K_w] and self.on_ground and not inventory.visible:
            self.vel.y = -9.2
            self.vel.x *= 1.133
            if self.vel.x > self.jumping_max_speed:
                self.vel.x = self.jumping_max_speed
            elif self.vel.x < -self.jumping_max_speed:
                self.vel.x = -self.jumping_max_speed
        if -SLIDE * dt < self.vel.x < SLIDE * dt:
            self.vel.x = 0
        if self.vel.x > 0:
            self.direction = "right"
        elif self.vel.x < 0:
            self.direction = "left"

        self.acc.y = GRAVITY
        self.vel += self.acc * dt
        if self.vel.y > TERMINAL_VEL:
            self.vel.y = TERMINAL_VEL
        if self.on_ground:
            if self.vel.x < 0:
                self.vel.x += 0.03 * dt
            elif self.vel.x > 0:
                self.vel.x -= 0.03 * dt
                
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
        self.rect.topleft = self.pos - camera.pos
        self.animate()

    def draw(self, screen):
        self.leg2.rect = self.leg2.image.get_rect(center=(self.rect.x+self.width/2, self.rect.y+72))
        screen.blit(self.leg2.image, self.leg2.rect.topleft)
        
        self.arm2.rect = self.arm2.image.get_rect(center=(self.rect.x+self.width/2, self.rect.y+35))
        screen.blit(self.arm2.image, self.arm2.rect.topleft)
        
        self.body.rect = self.body.image.get_rect(center=(self.rect.x+self.width/2, self.rect.y+51))
        screen.blit(self.body.image, self.body.rect.topleft)
        
        self.arm.rect = self.arm.image.get_rect(center=(self.rect.x+self.width/2, self.rect.y+35))
        screen.blit(self.arm.image, self.arm.rect.topleft)
        
        self.head.rect = self.head.image.get_rect(center=(self.rect.x+self.width/2, self.rect.y+23))
        screen.blit(self.head.image, self.head.rect.topleft)
        
        self.leg.rect = self.leg.image.get_rect(center=(self.rect.x+self.width/2, self.rect.y+72))
        screen.blit(self.leg.image, self.leg.rect.topleft)

    def animate(self):
        m_pos = vec(pygame.mouse.get_pos())
        self.head.rot = -vec(self.head.rect.center).angle_to(m_pos-vec(self.head.rect.center))-25
        
        if self.vel.x != 0:
            self.leg.count += 0.2 * dt
            if abs(self.vel.x) > self.max_speed * 1.05:
                self.leg.rot = cos(self.leg.count) * 40
            elif abs(self.vel.x) > self.max_speed * 0.5:
                self.leg.rot = cos(self.leg.count) * 30
            else:
                self.leg.rot = cos(self.leg.count) * 15
            self.leg2.rot = -self.leg.rot
            self.arm.rot = self.leg.rot * 0.8
            self.arm2.rot = -self.arm.rot
        else:
            self.leg.count = self.leg.rot = self.leg2.rot = self.arm.rot = self.arm2.rot = 0
            
        if abs(self.head.rot) < 90:
            rotate = pygame.transform.rotate
            self.head.image, self.body.image = rotate(player_head, self.head.rot), player_body
            self.arm.image, self.arm2.image = rotate(player_arm, self.arm.rot), rotate(player_arm, self.arm2.rot)
            self.leg.image, self.leg2.image = rotate(player_leg, self.leg.rot), rotate(player_leg, self.leg2.rot)
        else:
            rotate = pygame.transform.rotate
            self.head.image, self.body.image = rotate(invert_player_head, self.head.rot-180), invert_player_body
            self.arm.image, self.arm2.image = rotate(invert_player_arm, self.arm.rot), rotate(invert_player_arm, self.arm2.rot)
            self.leg.image, self.leg2.image = rotate(invert_player_leg, self.leg.rot), rotate(invert_player_leg, self.leg2.rot)

    def move(self):
        split = ceil(90/(clock.get_fps() or 1)*1.5)
        flag = False
        for _ in range(split):
            for y in range(4):
                for x in range(3):
                    if in_dict(blocks, (int(self.coords.x-1+x), int(self.coords.y-1+y))):
                        block = blocks[(int(self.coords.x-1+x), int(self.coords.y-1+y))]
                        if block.data["collision_box"] == "full":
                            if self.vel.y < 0:
                                if block_collide(floor(self.pos.x), floor(self.pos.y+self.vel.y/split), self.width, self.height, block):
                                    self.pos.y = floor(block.pos.y + BLOCK_SIZE)
                                    self.vel.y = 0
                                    flag = True
                            elif self.vel.y >= 0:
                                if self.vel.x <= 0:
                                    if block_collide(floor(self.pos.x), ceil(self.pos.y+self.vel.y/split), self.width, self.height, block):
                                        self.pos.y = ceil(block.pos.y - self.height)
                                        self.vel.y = 0
                                        flag = True
                                elif self.vel.x > 0:
                                    if block_collide(ceil(self.pos.x), ceil(self.pos.y+self.vel.y/split), self.width, self.height, block):
                                        self.pos.y = ceil(block.pos.y - self.height)
                                        self.vel.y = 0
                                        flag = True
            self.pos.y += self.vel.y * dt / split
            if flag: break
            
        flag = False
        for _ in range(split):
            for y in range(4):
                for x in range(3):
                    if in_dict(blocks, (int(self.coords.x-1+x), int(self.coords.y-1+y))):
                        block = blocks[(int(self.coords.x-1+x), int(self.coords.y-1+y))]
                        if block.data["collision_box"] == "full":
                            if self.vel.x < 0:
                                if block_collide(floor(self.pos.x+self.vel.x/split), floor(self.pos.y), self.width, self.height, block):
                                    self.pos.x = floor(block.pos.x + BLOCK_SIZE)
                                    self.vel.x = 0
                                    flag = True
                            elif self.vel.x >= 0:
                                if block_collide(ceil(self.pos.x+self.vel.x/split), ceil(self.pos.y), self.width, self.height, block):
                                    self.pos.x = ceil(block.pos.x - self.width)
                                    self.vel.x = 0
                                    flag = True
            self.pos.x += self.vel.x * dt / split
            if flag: break

class Particle(pygame.sprite.Sprite):
    def __init__(self, type, pos, master=None):
        pygame.sprite.Sprite.__init__(self)
        particles.append(self)
        self.type = type
        self.pos = vec(pos)
        self.coords = self.pos // BLOCK_SIZE
        
        if self.type == "block":
            self.size = randint(6, 8)
            self.image = pygame.Surface((self.size, self.size))
            self.vel = vec(randint(-35, 35)/10, randint(-30, 5)/10)
            if master:
                self.master = master
                color = self.master.image.get_at((randint(0, BLOCK_SIZE-1), randint(0, BLOCK_SIZE-1)))
                self.image.fill(color)
                if color == (255, 255, 255):
                    particles.remove(self)
                    self.kill()
                    
        self.timer = time.time()
        self.survive_time = randint(4, 8) / 10

    def update(self):
        if time.time() - self.timer > self.survive_time:
            particles.remove(self)
            self.kill()
            
        if in_dict(blocks, inttup(self.coords)):
            if blocks[inttup(self.coords)].data["collision_box"] == "none":
                self.vel.y += GRAVITY * dt
        else:
            self.vel.y += GRAVITY * dt
        self.vel.x *= 0.93
        
        neighbors = [
            inttup(self.coords),
            inttup((self.coords.x-1, self.coords.y)),
            inttup((self.coords.x+1, self.coords.y)),
            inttup((self.coords.x, self.coords.y-1)),
            inttup((self.coords.x, self.coords.y+1)),
        ]
        for pos in neighbors:
            if in_dict(blocks, pos):
                block = blocks[pos]
                if block.data["collision_box"] != "none":
                    if pygame.Rect(block.pos.x, block.pos.y, BLOCK_SIZE, BLOCK_SIZE).collidepoint(self.pos.x+self.vel.x*dt, self.pos.y):
                        self.vel.x = 0
                        break
                    if pygame.Rect(block.pos.x, block.pos.y, BLOCK_SIZE, BLOCK_SIZE).collidepoint(self.pos.x, self.pos.y+self.vel.y*dt):
                        self.vel.y = 0
                        break
                    
        self.pos += self.vel * dt
        self.coords = self.pos // BLOCK_SIZE
        
        if inttup(self.coords // CHUNK_SIZE) not in rendered_chunks:
            try: particles.remove(self)
            except: pass
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, (self.pos-camera.pos-vec(self.image.get_size())/2))

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
            "0 -1": inttup((self.coords.x, self.coords.y-1)),
            "0 1": inttup((self.coords.x, self.coords.y+1)),
            "-1 0": inttup((self.coords.x-1, self.coords.y)),
            "1 0": inttup((self.coords.x+1, self.coords.y))
        }
        self.image = block_textures[self.name]
        
        if self.data["collision_box"] == "full":
            self.rect = pygame.Rect(self.pos, (BLOCK_SIZE, BLOCK_SIZE))
        elif self.data["collision_box"] == "none":
            self.rect = pygame.Rect(self.pos, (0, 0))

    def update(self):
        if not is_supported(self.pos, self.data, self.neighbors):
            remove_blocks.append(self.coords)

    def draw(self, screen):
        self.rect.topleft = self.pos - camera.pos
        screen.blit(self.image, self.rect.topleft)

class Chunk(object):
    def __init__(self, pos):
        self.pos = pos
        self.block_data = generate_chunk(pos[0], pos[1])
        chunks[self.pos] = self

    def render(self):
        if self.pos in rendered_chunks:
            for block in self.block_data:
                if not in_dict(blocks, block):
                    blocks[block] = Block(self, block, self.block_data[block])
                blocks[block].draw(screen)

    def debug(self):
        pygame.draw.rect(screen, (255, 255, 0), (self.pos[0]*CHUNK_SIZE*BLOCK_SIZE-camera.pos[0], self.pos[1]*CHUNK_SIZE*BLOCK_SIZE-camera.pos[1], CHUNK_SIZE*BLOCK_SIZE, CHUNK_SIZE*BLOCK_SIZE), width=1)

class StructureGenerator(object):
    def __init__(self, folder, obstruction=False):
        self.folder = folder
        self.obstruction = obstruction
        self.files = structures[folder]
        self.distribution = structures[folder]["distribution"]
        self.block_data = {}
        
        max_sizes = []
        for file in self.files:
            if file != "distribution":
                self.block_data[file] = structures[folder][file]
                max_sizes.append((max(x for x, y in self.block_data[file][1]) - min(x for x, y in self.block_data[file][1]) + 1,
                            max(y for x, y in self.block_data[file][1]) - min(y for x, y in self.block_data[file][1]) + 1))
        self.max_size = max(max_sizes)
        
        self.chunks_to_check = int(ceil(self.max_size[0] / CHUNK_SIZE)), int(ceil(self.max_size[1] / CHUNK_SIZE))

    def generate(self, origin):
        seed(SEED + origin[0] * CHUNK_SIZE + origin[1] * CHUNK_SIZE)
        file = choices(self.distribution["files"], weights=self.distribution["weights"])[0]
        mirror = randint(0, 1)
        
        block_data = {
            (origin[0] + offset[0] if mirror else origin[0] - offset[0], origin[1] + offset[1]):
            (block if "," not in block else (choices([i.split("=")[0] for i in block.split(",")],
            weights=[int(i.split("=")[1]) for i in block.split(",")])[0]))
            for offset, block in self.block_data[file][1].items()
        }
        
        return block_data

class Item(object):
    def __init__(self, name):
        self.name = name
        self.count = 1
        self.nbt = {}

class Inventory(object):
    def __init__(self):
        self.slot_start = vec(400, 302)
        self.slot_size = (40, 40)
        self.items = {}
        self.hotbar = Hotbar(self)
        self.visible = False
        self.selected = None
        self.hovering = None
        self.transparent_background = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
        self.transparent_background.fill((0, 0, 0, 125))

    def update(self, m_state):
        if self.visible:
            mpos = vec(pygame.mouse.get_pos())
            y_test = self.slot_start.y < mpos.y < self.slot_start.y+(self.slot_size[1]+5)*3
            x_test = self.slot_start.x < mpos.x < self.slot_start.x+(self.slot_size[0]+5)*9
            hotbar_y_test = 446 < mpos.y < 446+(self.slot_size[1]+5)
            
            if y_test:
                self.hovering = inttup(((mpos.x-self.slot_start.x)//(self.slot_size[0]+5), (mpos.y-self.slot_start.y)//(self.slot_size[1]+5)+1))
            elif hotbar_y_test:
                self.hovering = inttup(((mpos.x-400)//(self.slot_size[0]+5), 0))
            else:
                self.hovering = None
            if m_state == 1 and (y_test or hotbar_y_test) and x_test:
                if in_dict(self.items, self.hovering):
                    if not self.selected:
                        self.selected = self.items[self.hovering]
                        self.clear_slot(self.hovering)
                    else:
                        tmp = self.selected
                        self.selected = self.items[self.hovering]
                        self.set_slot(self.hovering, tmp.name)
                else:
                    if self.selected:
                        self.set_slot(self.hovering, self.selected.name)
                        self.selected = None
                        
        if m_state == 4 or m_state == 5:
            self.hotbar.update(m_state)
        else:
            self.hotbar.update(0)

    def draw(self, screen):
        self.hotbar.draw(screen)
        if self.visible:
            screen.blit(self.transparent_background, (0, 0))
            screen.blit(inventory_img, (vec(SCR_DIM)/2-vec(inventory_img.get_width()/2, inventory_img.get_height()/2)))
            
            for slot in self.items:
                item_img = pygame.transform.scale(block_textures[self.items[slot].name], self.slot_size)
                if slot[1] != 0:
                    screen.blit(item_img, self.slot_start+vec(slot[0]*(self.slot_size[0]+5), (slot[1]-1)*(self.slot_size[1]+5)))
                else:
                    screen.blit(item_img, self.slot_start+vec(0, 190)+vec(slot[0]*(self.slot_size[0]+5), (slot[1]-1)*(self.slot_size[1]+5)))
            if self.selected:
                screen.blit(pygame.transform.scale(block_textures[self.selected.name], inttup(vec(self.slot_size)*0.9)), vec(pygame.mouse.get_pos())-vec(self.slot_size)*0.45)
            if in_dict(self.items, self.hovering):
                name = self.items[self.hovering].name.replace("_", " ").capitalize()
                mpos = pygame.mouse.get_pos()
                if self.selected == None:
                    blit_text_box(screen, smol_text(name), (mpos[0]+12, mpos[1]-24), 255)
                    
            player.leg2.rect = player.leg2.image.get_rect(center=(593+player.width/2, 140+72))
            screen.blit(player.leg2.image, player.leg2.rect.topleft)
            player.arm2.rect = player.arm2.image.get_rect(center=(593+player.width/2, 140+35))
            screen.blit(player.arm2.image, player.arm2.rect.topleft)
            player.body.rect = player.body.image.get_rect(center=(593+player.width/2, 140+51))
            screen.blit(player.body.image, player.body.rect.topleft)
            player.arm.rect = player.arm.image.get_rect(center=(593+player.width/2, 140+35))
            screen.blit(player.arm.image, player.arm.rect.topleft)
            player.head.rect = player.head.image.get_rect(center=(593+player.width/2, 140+23))
            screen.blit(player.head.image, player.head.rect.topleft)
            player.leg.rect = player.leg.image.get_rect(center=(593+player.width/2, 140+72))
            screen.blit(player.leg.image, player.leg.rect.topleft)

    def set_slot(self, slot, item):
        self.items[slot] = Item(item)

    def clear_slot(self, slot):
        del self.items[slot]

    def add_item(self, item):
        for y in range(4):
            for x in range(9):
                if not in_dict(self.items, (x, y)):
                    self.items[(x, y)] = Item(item)
                    return True
        return False

class Hotbar(object):
    def __init__(self, inventory):
        self.slot_start = vec(WIDTH/2-hotbar_img.get_width()/2, HEIGHT-hotbar_img.get_height())
        self.slot_size = (40, 40)
        self.inventory = inventory
        items = {}
        for slot in self.inventory.items:
            if slot[1] == 0:
                items[slot[0]] = self.inventory.items[slot]
        self.items = items
        self.selected = 0
        self.fade_timer = 0

    def update(self, scroll):
        hotbar_items = {}
        for slot in self.inventory.items:
            if slot[1] == 0:
                hotbar_items[slot[0]] = self.inventory.items[slot]

        self.items = hotbar_items
        if not self.inventory.visible:
            keys = pygame.key.get_pressed()
            for i in range(K_1, K_9+1):
                if keys[i]:
                    self.selected = i-K_0-1
                    self.fade_timer = time.time()
                    
            if scroll == 4:
                if self.selected == 0:
                    self.selected = 8
                else:
                    self.selected -= 1
            elif scroll == 5:
                if self.selected == 8:
                    self.selected = 0
                else:
                    self.selected += 1
                    
            if scroll:
                self.fade_timer = time.time()
                
        if in_dict(self.items, self.selected):
            player.holding = self.items[self.selected].name
        else:
            player.holding = None

    def draw(self, screen):
        screen.blit(hotbar_img, self.slot_start)
        screen.blit(hotbar_selection_img, (self.slot_start-vec(2, 2)+vec(self.slot_size[0]+10, 0)*self.selected))
        for slot in self.items:
            item_img = pygame.transform.scale(block_textures[self.items[slot].name], self.slot_size)
            screen.blit(item_img, self.slot_start+vec(8, 0)+vec(slot*(self.slot_size[0]+10), 8))
            
        if (time_elapsed := time.time() - self.fade_timer) < 3:
            if in_dict(self.items, self.selected):
                opacity = 255 * (3-time_elapsed) if time_elapsed > 2 else 255
                blitted_text = smol_text(self.items[self.selected].name.replace("_", " ").capitalize())
                blit_text_box(screen, blitted_text, (WIDTH/2-blitted_text.get_width()/2-8, HEIGHT-92), opacity)

class Crosshair():
    def __init__(self, changespeed) -> None:
        self.color = pygame.Color(0, 0, 0)
        self.changeover = changespeed
        
    def update(self, mpos):
        color = self.get_avg_color(mpos)
        if 127-30 < color.r < 127+30 and 127-30 < color.g < 127+30 and 127-30 < color.b < 127+30:
            color = pygame.Color(255, 255, 255)
        color = pygame.Color(255, 255, 255) - color

        # Modified version of this SO answer, thank you!
        # https://stackoverflow.com/a/51979708/17303382
        self.color = [x + (((y - x) / self.changeover) * 100 * dt) for x, y in zip(self.color, color)]

    def draw(self, screen, mpos) -> None:
        pygame.draw.rect(screen, self.color, (mpos[0]-2, mpos[1]-16, 4, 32))
        pygame.draw.rect(screen, self.color, (mpos[0]-16, mpos[1]-2, 32, 4))

    def get_avg_color(self, mpos) -> None:
        try:
            surf = screen.subsurface((mpos[0]-16, mpos[1]-16, 32, 32))
            color = pygame.Color(pygame.transform.average_color(surf))
        except:
            color = screen.get_at(inttup(mpos))

        return color

def get_structures(x: int, y: int, generator: StructureGenerator, chance: tuple) -> list:
    """Get structures inside the current chunk (x, y)

    Args:
        x (int): chunk position x
        y (int): chunk position y
        generator (StructureGenerator): structure object to generate
        chance (tuple): the odds of the structure generating, (number-of-structure-possible-per-chunk, odds-off-the-structure-generating-per-block-in-chunk)

    Returns:
        list: a list containing the block data of the structures in the chunk
    """
    out = []
    seed(SEED + x * CHUNK_SIZE + y * CHUNK_SIZE)
    for _ in range(chance[0]):
        if randint(0, chance[1]) == 0:
            block_x = x * CHUNK_SIZE + randrange(0, CHUNK_SIZE)
            # Generate on the surface of the world
            grass_y = terrain_generate(block_x)-1
            
            # If it is cut off by a cave, don't generate
            if (92.7 < cave_generate([block_x/70, grass_y/70]) < 100) or (92.7 < cave_generate([block_x/70, (grass_y+1)/70]) < 100):
                return out
            # Structures that are not in this chunk
            if not 0 <= grass_y - y * CHUNK_SIZE < CHUNK_SIZE:
                return out
            
            out.append(generator.generate((block_x, grass_y)))
    return out

def generate_structures(x: int, y: int, chunk_data: dict, generator: StructureGenerator, chance: tuple) -> dict:
    """Check the surrounding chunks for structures that generates in the current chunk (x, y), and then returns the chunk data with the structure

    Args:
        x (int): chunk position x
        y (int): chunk position y
        chunk_data (dict): original chunk data
        generator (StructureGenerator): the structure object to generate
        chance (tuple): the odds of the structure generating, (number-of-structure-possible-per-chunk, odds-of-a-chunk-containing-the-structure)

    Returns:
        dict: the chunk data with the structure
    """
    chunk_data_orig = chunk_data.copy()
    # Check all chunks around the current chunk within the size limit of the structure
    for ox in range(-generator.chunks_to_check[0], generator.chunks_to_check[0] + 1):
        for oy in range(-generator.chunks_to_check[1], generator.chunks_to_check[1] + 1):
            # Get the surrounding structures that might protrude into the current chunk
            structs = get_structures(x + ox, y + oy, generator, chance)
            for struct in structs:
                for block, block_name in struct.items():
                    # If there are parts of that structure inside the current chunk, generate that part in this chunk
                    if 0 <= block[0]-x*CHUNK_SIZE < CHUNK_SIZE and 0 <= block[1]-y*CHUNK_SIZE < CHUNK_SIZE:
                        if in_dict(chunk_data, block):
                            # Check if that position already has block and whether it can be overwritten by the structure
                            # i.e. leaves can replace grass but not grass blocks
                            if in_dict(block_data[block_name], "overwriteable"):
                                if chunk_data[block] in block_data[block_name]["overwriteable"]:
                                    chunk_data[block] = block_name
                                else:
                                    # Obstruction determines whether the struture can generate when there are non-overwriteable blocks in its way
                                    if generator.obstruction:
                                        return chunk_data_orig
                            else:
                                if not generator.obstruction:
                                    chunk_data[block] = block_name
                                else:
                                    return chunk_data_orig
                        else:
                            chunk_data[block] = block_name
    return chunk_data

def terrain_generate(x: int) -> float:
    """Takes the x position of a block and returns the height it has to be at"""
    return -int(noise.noise2d(x*0.1, 0)*5)+5

def cave_generate(coords: list) -> float:
    """Takes the coordinates of a block and returns the noise map value for cave generation"""
    noise_height = pnoise(coords)
    noise_height = noise_height + 0.5 if noise_height > 0 else 0
    noise_height = int(pow(noise_height * 255, 0.9))
    return noise_height

def generate_chunk(x: int, y: int) -> dict:
    """Takes the chunk coordinates and returns a dictionary containing the block data inside the chunk"""
    seed(x*CHUNK_SIZE+y*CHUNK_SIZE)
    chunk_data = {}
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target = (x * CHUNK_SIZE + x_pos, y * CHUNK_SIZE + y_pos)
            block_name = ""
            
            # Cave noise map
            cave_noise_map_coords = [target[0]/70, target[1]/70]
            # Don't generate blocks if it satifies a certain range of values in the cave noise map, AKA a cave
            cave_noise_map_value = cave_generate(cave_noise_map_coords)
            
            if not (92.7 < cave_noise_map_value < 100):
                # Generate terrain
                height = terrain_generate(target[0])
                if target[1] == height:
                    block_name = "grass_block"
                elif height+1 <= target[1] < height+4:
                    block_name = "dirt"
                elif target[1] >= height+4:
                    block_name = "stone"
                if target[1] == height-1:
                    if not (92.7 < cave_generate([target[0]/70, (target[1]+1)/70]) < 100):
                        if randint(0, 2) == 0:
                            block_name = "grass"
                        if randint(0, 21) == 0:
                            block_name = choices(["poppy", "dandelion"], weights=[1, 2])[0]
                if block_name != "":
                    chunk_data[target] = block_name

    # Generate structures
    generator = StructureGenerator("oak_tree", obstruction=False)
    chunk_data = generate_structures(x, y, chunk_data, generator, (1, 2))
    generator = StructureGenerator("tall_grass", obstruction=True)
    chunk_data = generate_structures(x, y, chunk_data, generator, (4, 3))
    return chunk_data

blocks = {}
chunks = {}
player = Player()
camera = Camera(player)
crosshair = Crosshair(1750)
particles = []
inventory = Inventory()
inventory.add_item("grass_block")
inventory.add_item("dirt")
inventory.add_item("stone")
inventory.add_item("grass")
inventory.add_item("oak_log")
inventory.add_item("oak_leaves")
inventory.add_item("oak_planks")
inventory.add_item("cobblestone")
inventory.add_item("glass")
inventory.add_item("poppy")
inventory.add_item("dandelion")
inventory.add_item("tall_grass")

pygame.mouse.set_visible(False)
remove_blocks = []

def draw(screen):
    screen.fill((135, 206, 250))
    mpos = vec(pygame.mouse.get_pos())
    block_pos = (player.pos+(mpos-player.rect.topleft))//BLOCK_SIZE
    for chunk in rendered_chunks:
        chunks[chunk].render()
    for particle in particles:
        particle.draw(screen)
    player.draw(screen)
    
    # Debug stuff
    if debug:
        for chunk in rendered_chunks:
            chunks[chunk].debug()
        pygame.draw.rect(screen, (255, 255, 255), player.rect, width=1)
        for rect in detecting_rects:
            pygame.draw.rect(screen, (255, 0, 0), rect, width=1)
        screen.blit(text(f"Seed: {SEED}"), (6, 0))
        screen.blit(text(f"Velocity: {(round(player.vel.x, 3), round(player.vel.y, 3))}"), (6, 24))
        screen.blit(text(f"Position: {inttup(player.coords)}"), (6, 48))
        screen.blit(text(f"Camera offset: {inttup(player.pos-camera.pos-vec(SCR_DIM)/2+player.size/2)}"), (6, 72))
        screen.blit(text(f"Chunk: {inttup(player.coords//CHUNK_SIZE)}"), (6, 96))
        screen.blit(text(f"Chunks loaded: {len(chunks)}"), (6, 120))
        screen.blit(text(f"Rendered blocks: {len(blocks)}"), (6, 144))
        if not inventory.visible:
            if in_dict(blocks, inttup(block_pos)):
                screen.blit(text(f"{blocks[inttup(block_pos)].name.replace('_', ' ')}", color=(255, 255, 255)), (mpos[0]+12, mpos[1]-36))
    
    inventory.draw(screen)
    if not inventory.visible:
        crosshair.draw(screen, mpos)

    pygame.display.flip()

running = True
debug = False

while running:
    dt = clock.tick_busy_loop(FPS) / 16
    if dt > 12: dt = 12
    pygame.display.set_caption(f"2D Minecraft | FPS: {int(clock.get_fps())}")
    
    mpos = vec(pygame.mouse.get_pos())
    
    mouse_state = 0
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            
        if event.type == MOUSEBUTTONDOWN:
            mouse_state = event.button
            if not inventory.visible:
                block_pos = inttup((player.pos+(mpos-player.rect.topleft))//BLOCK_SIZE)
                neighbors = {
                    "0 -1": inttup((block_pos[0], block_pos[1]-1)),
                    "0 1": inttup((block_pos[0], block_pos[1]+1)),
                    "-1 0": inttup((block_pos[0]-1, block_pos[1])),
                    "1 0": inttup((block_pos[0]+1, block_pos[1]))
                }
                
                if event.button == 1:
                    if in_dict(blocks, block_pos):
                        remove_block(block_pos, blocks[block_pos].data, neighbors)
                        
                if event.button == 3:
                    if player.holding:
                        if in_dict(block_data[player.holding], "counterparts"):
                            counterparts = block_data[player.holding]["counterparts"]
                            for counterpart in counterparts:
                                c_pos = vec(block_pos)+vec(inttup(counterpart.split(" ")))
                                c_neighbors = {
                                    "0 -1": inttup((c_pos.x, c_pos.y-1)),
                                    "0 1": inttup((c_pos.x, c_pos.y+1)),
                                    "-1 0": inttup((c_pos.x-1, c_pos.y)),
                                    "1 0": inttup((c_pos.x+1, c_pos.y))
                                }
                                if not is_placeable(c_pos, block_data[counterparts[counterpart]], c_neighbors, c=block_pos):
                                    break
                            else:
                                for counterpart in counterparts:
                                    if not is_placeable(block_pos, block_data[player.holding], neighbors, c=c_pos):
                                        break
                                else:
                                    set_block(block_pos, player.holding, neighbors)
                                    for counterpart in counterparts:
                                        c_pos = vec(block_pos)+vec(inttup(counterpart.split(" ")))
                                        c_neighbors = {
                                            "0 -1": inttup((c_pos.x, c_pos.y-1)),
                                            "0 1": inttup((c_pos.x, c_pos.y+1)),
                                            "-1 0": inttup((c_pos.x-1, c_pos.y)),
                                            "1 0": inttup((c_pos.x+1, c_pos.y))
                                        }
                                        set_block(vec(block_pos)+vec(inttup(counterpart.split(" "))), counterparts[counterpart], c_neighbors)
                        else:
                            if is_placeable(block_pos, block_data[player.holding], neighbors):
                                set_block(block_pos, player.holding, neighbors)
                                
        if event.type == KEYDOWN:
            if event.key == K_F5:
                debug = not debug
            if event.key == K_e:
                inventory.visible = not inventory.visible
                if inventory.visible:
                    pygame.mouse.set_visible(True)
                else:
                    pygame.mouse.set_visible(False)
                    if inventory.selected:
                        inventory.add_item(inventory.selected.name)
                        inventory.selected = None

    rendered_chunks = []
    for y in range(int(HEIGHT/(CHUNK_SIZE*BLOCK_SIZE)+2)):
        for x in range(int(WIDTH/(CHUNK_SIZE*BLOCK_SIZE)+2)):
            chunk = (
                x - 1 + int(round(camera.pos.x / (CHUNK_SIZE * BLOCK_SIZE))),
                y - 1 + int(round(camera.pos.y / (CHUNK_SIZE * BLOCK_SIZE)))
            )
            rendered_chunks.append(chunk)
            if chunk not in chunks:
                chunks[chunk] = Chunk(chunk)
                
    unrendered_chunks = []
    for y in range(int(HEIGHT/(CHUNK_SIZE*BLOCK_SIZE)+4)):
        for x in range(int(WIDTH/(CHUNK_SIZE*BLOCK_SIZE)+4)):
            chunk = (
                x - 2 + int(round(camera.pos.x / (CHUNK_SIZE * BLOCK_SIZE))),
                y - 2 + int(round(camera.pos.y / (CHUNK_SIZE * BLOCK_SIZE)))
            )
            if in_dict(chunks, chunk):
                if chunk not in rendered_chunks:
                    unrendered_chunks.append(chunk)
                    
    for chunk in unrendered_chunks:
        for block in chunks[chunk].block_data:
            if block in blocks:
                blocks[block].kill()
                del blocks[block]
                
    for block in remove_blocks:
        neighbors = {
            "0 -1": inttup((block[0], block[1]-1)),
            "0 1": inttup((block[0], block[1]+1)),
            "-1 0": inttup((block[0]-1, block[1])),
            "1 0": inttup((block[0]+1, block[1]))
        }
        remove_block(block, blocks[inttup(block)].data, neighbors)
        
    remove_blocks = []
    detecting_rects = []

    camera.update()
    player.update()
    for particle in particles:
        particle.update()
    inventory.update(mouse_state)
    crosshair.update(mpos)
    
    draw(screen)

pygame.quit()
quit()
