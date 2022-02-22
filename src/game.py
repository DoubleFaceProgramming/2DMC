from sys import exit as sysexit
from pathlib import Path
from random import seed
from enum import Enum
import datetime
import pygame
import os

from pygame.locals import  (
    K_e, K_F5, K_F9, K_F2, K_F3,
    MOUSEBUTTONDOWN, KEYDOWN,
    HWSURFACE, DOUBLEBUF,
    QUIT,
)

from src.constants import SCREENSHOTS_DIR, SEED, WIDTH, HEIGHT, FPS, SCR_DIM, VEC, CHUNK_SIZE, BLOCK_SIZE, SPACING, CustomEvents
from src.world_gen import Chunk, Block, load_chunks
from src.sprite import LayersEnum, SPRITE_MANAGER
from src.utils import inttup, text, CyclicalList
from src.background import Background
from src.particle import Particle
from src.player import Player

import src.utils as utils # For doing utils.do_profile ¯\_(ツ)_/¯

class GameManager():
    """For ultimate Karen mode"""

    instances = []

    def __init__(self) -> None:
        pygame.init()

        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50, 50)
        pygame.display.set_caption("2D Minecraft")
        pygame.mouse.set_visible(False)
        pygame.event.set_allowed([MOUSEBUTTONDOWN, KEYDOWN, QUIT, *[event.value for event in CustomEvents]])

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE | DOUBLEBUF)

        self.cinematic_modes = iter(CyclicalList([mode.value for mode in self.__class__.CinematicModes]))
        self.cinematic = self.__class__.CinematicModes.BOTH

    def new(self):
        self.__class__.instances.append(game := Game(self))
        return game

    def screenshot(self, game) -> None:
        screenshot_path = Path(os.path.join(SCREENSHOTS_DIR, str(datetime.datetime.now().strftime("2DMC_%Y-%m-%d_%H.%M.%S.png"))))
        # If the screenshots folder doesn't exist
        if not (screenshots_dir := screenshot_path.parent).exists():
            screenshots_dir.mkdir()
        pygame.image.save(game.screen, screenshot_path)

    def cycle_cinematic(self) -> None:
        self.cinematic = self.__class__.CinematicModes(next(self.cinematic_modes))

    class CinematicModes(Enum):
        """An Enum that stores the options for the cinematic modes cycle/toggle
        CH is whether the crosshair shows, HB is whether the hotbar shows"""
        BOTH = {"CH": True, "HB": True}
        NEITHER = {"CH": False, "HB": False}
        CROSSHAIR = {"CH": True, "HB": False}
        HOTBAR = {"CH": False, "HB": True}

class Game():
    """Class that handles events and function calls to other classes to run the game"""

    def __init__(self, manager: GameManager) -> None:
        seed(SEED)

        self.manager = manager
        self.screen = self.manager.screen

        self.player = Player(LayersEnum.PLAYER)
        self.background = Background()
        self.clock = pygame.time.Clock()
        self.rendered_chunks = []
        self.debug_bool = False
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
                # Toggles and functionalities
                if event.key == K_F5:
                    self.debug_bool = not self.debug_bool
                if event.key == K_F9:
                    utils.do_profile = True
                if event.key == K_e:
                    self.player.toggle_inventory()
                if event.key == K_F2:
                    self.manager.screenshot(self)
                if event.key == K_F3:
                    self.manager.cycle_cinematic()

        # Loading chunks
        self.rendered_chunks = load_chunks(self.player.camera)
        # Calling relevant update functions.
        SPRITE_MANAGER.update(dt, m_state=mouse_state, blocks=Block.instances, camera=self.player.camera, rendered_chunks=self.rendered_chunks, player_y=self.player.coords.y)

    def draw(self) -> None:
        # Drawing all sprites!
        SPRITE_MANAGER.draw(self.screen, self.debug_bool, camera=self.player.camera, rendered_chunks=self.rendered_chunks)

    def debug(self, mpos) -> None:
        if not self.debug_bool: return

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

        # Displaying the debug values.
        for line, name in enumerate(debug_values):
            self.screen.blit(text(f"{name}: {debug_values[name]}"), (6, SPACING * line))

    def tick(self, mpos):
        """Ticks the game loop (makes profiling a bit easier)"""

        self.update(mpos)
        self.draw()
        self.debug(mpos)

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