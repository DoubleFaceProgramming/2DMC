from sys import exit as sysexit
from random import seed
from math import cos, pi
import pygame
import os
from pygame.locals import  (
    MOUSEBUTTONDOWN, KEYDOWN,
    HWSURFACE, DOUBLEBUF,
    K_e, K_F5,
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
    """Class that handles events and function calls to other classes to run the game"""

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
                # Placing, breaking and pickblocking blocks
                mouse_state = event.button
                if not self.player.inventory.visible:
                    if event.button == 1:
                        self.player.break_block(Chunk.instances, mpos)
                    elif event.button == 2:
                        self.player.pick_block(mpos)
                    elif event.button == 3:
                        self.player.place_block(Chunk.instances, mpos)

            if event.type == KEYDOWN:
                # Toggling debug mode and the player inventory
                if event.key == K_F5:
                    self.debug_bool = not self.debug_bool
                if event.key == K_e:
                    self.player.toggle_inventory()

        # Calling relevant update functions.
        self.rendered_chunks = load_chunks(self.player.camera)
        self.player.update(Block.instances, mouse_state, dt)
        for particle in Particle.instances:
            particle.update(Block.instances, dt)
        for chunk in self.rendered_chunks:
            Chunk.instances[chunk].update(self.player.camera)

    def draw(self, screen, mpos) -> None:
        # Ik this shouldnt be a one liner but I couldn't resist (it looks so coool :DDDD)
        # Basiclaly a modified version of the crosshair colour changer, but this will always display blue
        # at y > 0, black at y <= 1024 (world limit) and anywhere inbetween it is a "gradient" of sorts.
        # Go from y = 0 -> y = 1024 ingame and you will understand what it does xD
        screen.fill(color if min((color := ([old + (new - old) * ((3.2 * (y_perc := self.player.coords.y / MAX_Y) ** 3 - 6.16 * y_perc ** 2 + 4.13 * y_perc) / 1.17) for old, new in zip(BLUE_SKY, (0, 0, 0))]) if self.player.coords.y > 0 else BLUE_SKY)) > 0 else (0, 0, 0))
        # Calling relevant draw functions.
        for chunk in self.rendered_chunks:
            Chunk.instances[chunk].draw(self.player.camera, screen)
        for particle in Particle.instances:
            particle.draw(self.player.camera, screen)

        self.player.draw(screen, mpos)
        
        if self.debug_bool:
            self.debug(self.screen, mpos)
                
        self.player.inventory.draw(screen)
        if not self.player.inventory.visible:
            self.player.crosshair.draw(screen, mpos)

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
            "Block position": inttup((self.player.pos + (mpos - self.player.rect.topleft)) // BLOCK_SIZE),
            "Detecting rects": len(self.player.detecting_rects),
            "Particles": len(Particle.instances),
        }

        # Calling the relevant debug functions.
        self.player.debug(screen, mpos)
        for chunk in self.rendered_chunks:
            Chunk.instances[chunk].debug(screen)

        # Displaying the debug values.
        for line, name in enumerate(debug_values):
            screen.blit(text(f"{name}: {debug_values[name]}"), (6, SPACING * line))

    def run(self) -> None:
        """Start the main loop of the game, which handles the calling of other functions."""
        while self.running:
            mpos = VEC(pygame.mouse.get_pos())

            self.update(mpos)
            self.draw(self.screen, mpos)

            pygame.display.flip()

        self.quit()

    def quit(self) -> None:
        """Call quit functions & cleanup."""
        pygame.quit()
        sysexit()