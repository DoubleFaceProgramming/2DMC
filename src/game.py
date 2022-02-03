from sys import exit as sysexit
from random import seed, randint
import pygame
import os

from pygame.locals import  (
    MOUSEBUTTONDOWN, KEYDOWN,
    K_e, K_F5, K_F9, K_F2,
    HWSURFACE, DOUBLEBUF,
    QUIT,
)

from src.constants import SEED, WIDTH, HEIGHT, FPS, SCR_DIM, VEC, CHUNK_SIZE, BLOCK_SIZE, SPACING
from src.particle import Particle, VoidFogParticle, EnvironmentalParticle, background_particles
from src.world_gen import Chunk, Block, load_chunks
from src.background import Background
from src.utils import inttup, text
from src.player import Player
import src.utils as utils

class Game():
    """Class that handles events and function calls to other classes to run the game"""

    def __init__(self) -> None:
        pygame.init()

        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50, 50)
        pygame.display.set_caption("2D Minecraft")
        pygame.mouse.set_visible(False)
        pygame.event.set_allowed([MOUSEBUTTONDOWN, KEYDOWN, QUIT])

        seed(SEED)

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE | DOUBLEBUF)
        self.background = Background()
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
                        self.player.pick_block()
                    elif event.button == 3:
                        self.player.place_block(Chunk.instances, mpos)

            if event.type == KEYDOWN:
                # Toggling debug mode and the player inventory
                if event.key == K_F5:
                    self.debug_bool = not self.debug_bool
                if event.key == K_F9:
                    utils.profile_bool = True
                if event.key == K_F2:
                    VoidFogParticle(self.player.pos, Block.instances)
                if event.key == K_e:
                    self.player.toggle_inventory()

        # Calling relevant update functions.
        self.background.update(dt, self.player.coords.y, self.player.camera)
        self.rendered_chunks = load_chunks(self.player.camera)
        self.player.update(Block.instances, mouse_state, dt)
        for particle in Particle.instances:
            particle.update(dt, self.player.camera)
        for chunk in self.rendered_chunks:
            Chunk.instances[chunk].update(self.player.camera)

    def draw(self, screen, mpos) -> None:
        # Clears the frame + also drawing the sky
        self.background.draw(screen, self.player.camera)

        # Calling relevant draw functions.
        for chunk in self.rendered_chunks:
            Chunk.instances[chunk].draw(self.player.camera, screen)

        for particle in Particle.instances:
            if not issubclass(particle.__class__, background_particles):
                particle.draw(screen, self.player.camera)

        self.player.draw(screen, mpos)

        if self.debug_bool:
            self.debug(self.screen, mpos)

        if not self.player.inventory.visible:
            self.player.crosshair.block_selection.draw(screen)
        self.player.inventory.draw(screen)
        if not self.player.inventory.visible:
            self.player.crosshair.draw(screen)

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
        self.player.debug(screen)
        for chunk in self.rendered_chunks:
            Chunk.instances[chunk].debug(screen)

        # Displaying the debug values.
        for line, name in enumerate(debug_values):
            screen.blit(text(f"{name}: {debug_values[name]}"), (6, SPACING * line))

        for particle in Particle.instances:
            pygame.draw.circle(screen, (255, 0, 0), particle.pos, radius=3)
            # pygame.draw.rect(screen, (255, 0, 0), particle.image.get_rect())

    def tick(self, mpos):
        """Ticks the game loop (makes profiling a bit easier)"""

        self.update(mpos)
        self.draw(self.screen, mpos)

    def run(self) -> None:
        """Start the main loop of the game, which handles the calling of other functions."""

        while self.running:
            mpos = VEC(pygame.mouse.get_pos())
            self.tick(mpos)
            pygame.display.flip()

        self.quit()

    def quit(self) -> None:
        """Call quit functions & cleanup."""
        pygame.quit()
        sysexit()