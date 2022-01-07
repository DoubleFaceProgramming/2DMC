from sys import exit as sysexit
from random import seed
import pygame
import os
from pygame.locals import  (
    MOUSEBUTTONDOWN, KEYDOWN,
    HWSURFACE, DOUBLEBUF,
    K_e, K_c, K_F5,
    QUIT,
)
from src.inventory import Item
from src.player import *
from src.particle import *
from src.constants import *
from src.utils import *
from src.block import *
from src.world_gen import *

class Game():
    def __init__(self) -> None:
        pygame.init()

        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50, 50)
        pygame.display.set_caption("2D Minecraft")
        pygame.mouse.set_visible(False)
        
        seed(SEED)

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE | DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.rendered_chunks = []
        self.debug_bool = False
        self.player = Player()
        self.running = True

    def update(self, mpos) -> None:
        dt = self.clock.tick_busy_loop(FPS) / 16
        if dt > 12: dt = 12
        
        mouse_state = 0
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                
            if event.type == MOUSEBUTTONDOWN:
                # Placing and breaking blocks
                mouse_state = event.button
                if not self.player.inventory.visible:
                    if event.button == 1:
                        self.player.break_block(Chunk.instances, mpos)
                    elif event.button == 3:
                        self.player.place_block(Chunk.instances, mpos)
        
            if event.type == KEYDOWN:
                # Toggling debug mode and the player inventory
                if event.key == K_F5:
                    self.debug_bool = not self.debug_bool
                if event.key == K_e:
                    self.player.toggle_inventory()
                if event.key == K_c:
                    self.player.pick_block(mpos)

        # Calling relevant update functions.
        self.rendered_chunks = load_chunks(self.player.camera)
        self.player.update(Block.instances, mouse_state, dt)
        for particle in Particle.instances:
            particle.update(Block.instances, dt)
        for chunk in self.rendered_chunks:
            Chunk.instances[chunk].update(self.player.camera)
        
    def draw(self, screen, mpos) -> None:
        screen.fill((135, 206, 250))
        
        # Calling relevant draw functions.
        for chunk in self.rendered_chunks:
            Chunk.instances[chunk].draw(self.player.camera, screen)
        for particle in Particle.instances:
            particle.draw(self.player.camera, screen)
            
        self.player.draw(screen, mpos)
        
    def debug(self, screen, mpos) -> None:
        # Generating some debug values and storing in a dict for easy access.
        debug_values = {
            "FPS": int(self.clock.get_fps()),
            "Seed": SEED, 
            "Velocity": (round(self.player.vel.x, 3), round(self.player.vel.y, 3)),
            "Positon": inttup(self.player.coords),
            "Camera offset": inttup(self.player.pos - self.player.camera.pos - VEC(SCR_DIM) / 2 + self.player.size / 2),
            "Chunk": inttup(self.player.coords // CHUNK_SIZE),
            "Chunks loaded": len(Chunk.instances),
            "Rendered blocks": len(Block.instances),
            "Block position": inttup((self.player.pos + (mpos - self.player.rect.topleft)) // BLOCK_SIZE)
        }
        
        # Calling the relevant debug functions.
        self.player.debug(screen, mpos)
        for chunk in self.rendered_chunks:
            Chunk.instances[chunk].debug(screen)  
            
        # Displaying the debug values.
        for line, name in enumerate(debug_values):
            screen.blit(text(f"{name}: {debug_values[name]}"), (6, SPACING * line))
        
    def run(self) -> None:
        """Start the main loop of the game, whcih handles the calling of other functions."""
        while self.running:
            mpos = VEC(pygame.mouse.get_pos())
            
            self.update(mpos)
            self.draw(self.screen, mpos)
            if self.debug_bool:
                self.debug(self.screen, mpos)
                
            pygame.display.flip()
                
        self.quit()
                        
    def quit(self) -> None:
        """Call quit functions & cleanup."""
        pygame.quit()
        sysexit()