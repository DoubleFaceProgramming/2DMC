from sys import exit as sysexit
from random import seed, randint
from pathlib import Path
import datetime
import pygame
import os

from pygame.locals import  (
    K_e, K_F5, K_F9, K_F2, K_F3,
    MOUSEBUTTONDOWN, KEYDOWN,
    HWSURFACE, DOUBLEBUF,
    QUIT,
)

from src.constants import SCREENSHOTS_DIR, SEED, WIDTH, HEIGHT, FPS, SCR_DIM, VEC, CHUNK_SIZE, BLOCK_SIZE, SPACING
from src.particle import Particle, background_particles
from src.world_gen import Chunk, Block, load_chunks
from src.background import Background
from src.utils import inttup, text
from src.player import Player
import src.utils as utils

class GameManager():
    """For ultimate Karen mode"""

    instances = []

    def __init__(self) -> None:
        pygame.init()

        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50, 50)
        pygame.display.set_caption("2D Minecraft")
        pygame.mouse.set_visible(False)
        pygame.event.set_allowed([MOUSEBUTTONDOWN, KEYDOWN, QUIT])

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE | DOUBLEBUF)
        self.cinematic = False

    def new(self):
        self.__class__.instances.append(game := Game(self))
        return game

    def screenshot(self, game) -> None:
        screenshot_path = Path(os.path.join(SCREENSHOTS_DIR, str(datetime.datetime.now().strftime("2DMC_%Y-%m-%d_%H.%M.%S.png"))))
        # If the screenshots folder doesn't exist
        if not (screenshots_dir := screenshot_path.parent).exists():
            screenshots_dir.mkdir()
        pygame.image.save(game.screen, screenshot_path)
        
    def toggle_cinematic(self) -> None:
        self.cinematic = not self.cinematic

class Game():
    """Class that handles events and function calls to other classes to run the game"""

    def __init__(self, manager: GameManager) -> None:
        seed(SEED)

        self.manager = manager
        self.screen = self.manager.screen
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
                    utils.do_profile = True
                if event.key == K_e:
                    self.player.toggle_inventory()
                if event.key == K_F2:
                    self.manager.screenshot(self)
                if event.key == K_F3:
                    self.manager.toggle_cinematic()

        # Calling relevant update functions.
        self.background.update(self.player.coords.y, self.player.camera)
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

        # We do not draw particles that are instances of or subclasses of
        # a background particle (defined in particle.py)
        for particle in Particle.instances:
            if not issubclass(particle.__class__, background_particles):
                particle.draw(screen, self.player.camera)

        if not self.manager.cinematic:
            if not self.player.inventory.visible:
                self.player.crosshair.block_selection.draw(screen)
        self.player.draw(screen)

        if self.debug_bool:
            self.debug(self.screen, mpos)

        if not self.manager.cinematic:
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
            "Detecting rects": len(self.player.detecting_blocks),
            "Particles": len(Particle.instances),
        }

        # Calling the relevant debug functions.
        self.player.debug(screen)
        for chunk in self.rendered_chunks:
            Chunk.instances[chunk].debug(screen)

        # Displaying the debug values.
        for line, name in enumerate(debug_values):
            screen.blit(text(f"{name}: {debug_values[name]}"), (6, SPACING * line))

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