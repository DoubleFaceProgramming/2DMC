from sys import exit as sysexit
from random import seed
import pygame
import os
from pygame.locals import  (
    MOUSEBUTTONDOWN, KEYDOWN,
    HWSURFACE, DOUBLEBUF,
    K_e, K_F5,
    QUIT,
)

from src.constants import *
from src.utils import *
from src.images import *
from src.player import Player
from src.particle import Particle
from src.block import *
from src.world_gen import Chunk, load_chunks

def loading():
    font = pygame.font.Font(REGULAR_FONT_LOC, 120)
    textsurface = font.render("Generating World...", True, (255, 255, 255))
    screen.blit(textsurface, (50, 200))
    pygame.display.flip()

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50, 50)
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE | DOUBLEBUF)
pygame.display.set_caption("2D Minecraft")
loading()
clock = pygame.time.Clock()
mixer = pygame.mixer.init()
seed(SEED)

player = Player()

pygame.mouse.set_visible(False)
remove_blocks = []

def draw(screen):
    screen.fill((135, 206, 250))
    mpos = VEC(pygame.mouse.get_pos())
    for chunk in rendered_chunks:
        Chunk.instances[chunk].draw(player.camera, screen)
    for particle in Particle.instances:
        particle.draw(player.camera, screen)
    player.draw(screen)
    
    # Debug stuff
    if debug:
        draw_debug(screen)
    
    player.inventory.draw(screen)
    if not player.inventory.visible:
        player.crosshair.draw(screen, mpos)

    pygame.display.flip()
    
def draw_debug(screen) -> None:
    # Draw chunk outline
    for chunk in rendered_chunks:
        Chunk.instances[chunk].debug(screen)
    # Draw player rect
    pygame.draw.rect(screen, (255, 255, 255), player.rect, width=1)
    # Display the blocks that the player is currently calculating collision with
    for rect in player.detecting_rects:
        pygame.draw.rect(screen, (255, 0, 0), rect, width=1)
    
    block_pos = (player.pos + (mpos - player.rect.topleft)) // BLOCK_SIZE
    debug_values = {
        "FPS": int(clock.get_fps()),
        "Seed": SEED, 
        "Velocity": (round(player.vel.x, 3), round(player.vel.y, 3)),
        "Positon": inttup(player.coords),
        "Camera offset": inttup(player.pos-player.camera.pos-VEC(SCR_DIM)/2+player.size/2),
        "Chunk": inttup(player.coords//CHUNK_SIZE),
        "Chunks loaded": len(Chunk.instances),
        "Rendered blocks": len(Block.instances),
        "Block position": inttup(block_pos)
    }
    
    for line, name in enumerate(debug_values):
        screen.blit(text(f"{name}: {debug_values[name]}"), (6, SPACING * line))
        
    if not player.inventory.visible:
        if inttup(block_pos) in Block.instances:
            screen.blit(text(f"{Block.instances[inttup(block_pos)].name.replace('_', ' ')}", color=(255, 255, 255)), (mpos[0]+12, mpos[1]-36))

running = True
debug = False

while running:
    dt = clock.tick_busy_loop(FPS) / 16
    if dt > 12: dt = 12
    pygame.display.set_caption(f"2D Minecraft")
    
    mpos = VEC(pygame.mouse.get_pos())
    mouse_state = 0
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            
        if event.type == MOUSEBUTTONDOWN:
            mouse_state = event.button
            if not player.inventory.visible:
                if event.button == 1:
                    player.break_block(Chunk.instances, mpos)
                elif event.button == 3:
                    player.place_block(Chunk.instances, mpos)
    
        if event.type == KEYDOWN:
            if event.key == K_F5:
                debug = not debug
            if event.key == K_e:
                player.toggle_inventory()

    rendered_chunks = load_chunks(player.camera)
                
    for block in remove_blocks:
        neighbors = {
            "0 -1": inttup((block[0], block[1]-1)),
            "0 1": inttup((block[0], block[1]+1)),
            "-1 0": inttup((block[0]-1, block[1])),
            "1 0": inttup((block[0]+1, block[1]))
        }
        remove_block(Chunk.instances, block, Block.instances[inttup(block)].data, neighbors)
        
    remove_blocks = []
    detecting_rects = []

    player.update(Block.instances, mouse_state, dt)
    for particle in Particle.instances:
        particle.update(Block.instances, dt)
    for chunk in rendered_chunks:
        Chunk.instances[chunk].update(player.camera)
    
    draw(screen)

pygame.quit()
sysexit()