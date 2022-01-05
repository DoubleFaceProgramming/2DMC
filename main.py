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
from src.world_gen import Chunk

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

blocks = {}
chunks = {}
player = Player()

pygame.mouse.set_visible(False)
remove_blocks = []

def draw(screen):
    screen.fill((135, 206, 250))
    mpos = VEC(pygame.mouse.get_pos())
    block_pos = (player.pos+(mpos-player.rect.topleft))//BLOCK_SIZE
    for chunk in rendered_chunks:
        chunks[chunk].draw()
    for particle in Particle.instances:
        particle.draw(player.camera, screen)
    player.draw(screen)
    
    # Debug stuff
    if debug:
        screen.blit(text(f"Seed: {SEED}"), (6, 0))
        screen.blit(text(f"Velocity: {(round(player.vel.x, 3), round(player.vel.y, 3))}"), (6, 24))
        screen.blit(text(f"Position: {inttup(player.coords)}"), (6, 48))
        screen.blit(text(f"Camera offset: {inttup(player.pos-player.camera.pos-VEC(SCR_DIM)/2+player.size/2)}"), (6, 72))
        screen.blit(text(f"Chunk: {inttup(player.coords//CHUNK_SIZE)}"), (6, 96))
        screen.blit(text(f"Chunks loaded: {len(chunks)}"), (6, 120))
        screen.blit(text(f"Rendered blocks: {len(blocks)}"), (6, 144))
        screen.blit(text(f"FPS: {len(blocks)}"), (6, 144))
        if not player.inventory.visible:
            if inttup(block_pos) in blocks:
                screen.blit(text(f"{blocks[inttup(block_pos)].name.replace('_', ' ')}", color=(255, 255, 255)), (mpos[0]+12, mpos[1]-36))
    
    player.inventory.draw(screen)
    if not player.inventory.visible:
        player.crosshair.draw(screen, mpos)

    pygame.display.flip()
    
def debug() -> None:
    # Draw chunk outline
    for chunk in rendered_chunks:
        chunks[chunk].debug()
    # Draw player rect
    pygame.draw.rect(screen, (255, 255, 255), player.rect, width=1)
    # Display the blocks that the player is currently calculating collision with
    for rect in player.detecting_rects:
        pygame.draw.rect(screen, (255, 0, 0), rect, width=1)

    debug_values = {
        "FPS": int(clock.get_fps()),
        "Seed": SEED, 
        "Velocity": (round(player.vel.x, 3), round(player.vel.y, 3)),
        "Positon": inttup(player.coords),
        "Camera offset": inttup(player.pos-player.camera.pos-VEC(SCR_DIM)/2+player.size/2),
        "Chunk": inttup(player.coords//CHUNK_SIZE),
        "Chunks loaded": len(chunks),
        "Rendered blocks": len(blocks)
    }
    
    for line, name in enumerate(debug_values):
        screen.blit(text(f"{name}: {debug_values[name]}"), (6, SPACING * line))

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
                block_pos = inttup((player.pos+(mpos-player.rect.topleft))//BLOCK_SIZE)
                neighbors = {
                    "0 -1": inttup((block_pos[0], block_pos[1]-1)),
                    "0 1": inttup((block_pos[0], block_pos[1]+1)),
                    "-1 0": inttup((block_pos[0]-1, block_pos[1])),
                    "1 0": inttup((block_pos[0]+1, block_pos[1]))
                }
                
                if event.button == 1:
                    if block_pos in blocks:
                        remove_block(block_pos, blocks[block_pos].data, neighbors)
                        
                if event.button == 3:
                    if player.holding:
                        if "counterparts" in BLOCK_DATA[player.holding]:
                            counterparts = BLOCK_DATA[player.holding]["counterparts"]
                            for counterpart in counterparts:
                                c_pos = VEC(block_pos)+VEC(inttup(counterpart.split(" ")))
                                c_neighbors = {
                                    "0 -1": inttup((c_pos.x, c_pos.y-1)),
                                    "0 1": inttup((c_pos.x, c_pos.y+1)),
                                    "-1 0": inttup((c_pos.x-1, c_pos.y)),
                                    "1 0": inttup((c_pos.x+1, c_pos.y))
                                }
                                if not is_placeable(c_pos, BLOCK_DATA[counterparts[counterpart]], c_neighbors, c=block_pos):
                                    break
                            else:
                                for counterpart in counterparts:
                                    if not is_placeable(block_pos, BLOCK_DATA[player.holding], neighbors, c=c_pos):
                                        break
                                else:
                                    set_block(block_pos, player.holding, neighbors)
                                    for counterpart in counterparts:
                                        c_pos = VEC(block_pos)+VEC(inttup(counterpart.split(" ")))
                                        c_neighbors = {
                                            "0 -1": inttup((c_pos.x, c_pos.y-1)),
                                            "0 1": inttup((c_pos.x, c_pos.y+1)),
                                            "-1 0": inttup((c_pos.x-1, c_pos.y)),
                                            "1 0": inttup((c_pos.x+1, c_pos.y))
                                        }
                                        set_block(VEC(block_pos)+VEC(inttup(counterpart.split(" "))), counterparts[counterpart], c_neighbors)
                        else:
                            if is_placeable(block_pos, BLOCK_DATA[player.holding], neighbors):
                                set_block(block_pos, player.holding, neighbors)
                                
        if event.type == KEYDOWN:
            if event.key == K_F5:
                debug = not debug
            if event.key == K_e:
                player.inventory.visible = not player.inventory.visible
                if player.inventory.visible:
                    pygame.mouse.set_visible(True)
                else:
                    pygame.mouse.set_visible(False)
                    if player.inventory.selected:
                        player.inventory.add_item(player.inventory.selected.name)
                        player.inventory.selected = None

    rendered_chunks = []
    for y in range(int(HEIGHT/(CHUNK_SIZE*BLOCK_SIZE)+2)):
        for x in range(int(WIDTH/(CHUNK_SIZE*BLOCK_SIZE)+2)):
            chunk = (
                x - 1 + int(round(player.camera.pos.x / (CHUNK_SIZE * BLOCK_SIZE))),
                y - 1 + int(round(player.camera.pos.y / (CHUNK_SIZE * BLOCK_SIZE)))
            )
            rendered_chunks.append(chunk)
            if chunk not in chunks:
                chunks[chunk] = Chunk(chunk)
                
    unrendered_chunks = []
    for y in range(int(HEIGHT/(CHUNK_SIZE*BLOCK_SIZE)+4)):
        for x in range(int(WIDTH/(CHUNK_SIZE*BLOCK_SIZE)+4)):
            chunk = (
                x - 2 + int(round(player.camera.pos.x / (CHUNK_SIZE * BLOCK_SIZE))),
                y - 2 + int(round(player.camera.pos.y / (CHUNK_SIZE * BLOCK_SIZE)))
            )
            if chunk in chunks:
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

    player.update(blocks, mouse_state, dt)
    for particle in Particle.instances:
        particle.update(blocks, dt)
    
    if debug: debug()
    draw(screen)

pygame.quit()
sysexit()