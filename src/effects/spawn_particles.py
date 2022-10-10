from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING: # Type annotations without causing circular imports
    from src.management.game_manager import GameManager
    from src.common.utils import WorldSlices
    from src.world.block import Location
    from types import LambdaType

from random import randint, uniform
from dataclasses import dataclass
from types import LambdaType
from pygame import Rect, Surface
import time

from src.effects.particles import BlockParticle, AtmosphericParticle
from src.common.constants import BLOCK_SIZE, SCR_DIM, VEC, MAX_Y
from src.common.utils import to_pps, WorldSlices, sign
from src.common.clamps import clamp_max

@dataclass
class GradualData:
    _freq_raw: tuple[float, float] | float | Callable

    def __post_init__(self):
        self.next_freq = uniform(*self.freq)
        self.start_time = time.time()

    @property
    def freq(self):
        # Allows freq to be given as a (lower, upper) *or* (lower, lower) (ie. will always be lower)
        if isinstance(self._freq_raw, float):
            return (self._freq_raw, self._freq_raw)
        return self._freq_raw

    def gradual_spawn(self, condition: bool) -> int:
        if not condition:
            self.start_time = time.time()
            return 0

        elapsed = time.time() - self.start_time
        if elapsed < self.next_freq: return 0

        self.next_freq = uniform(*self.freq)
        self.start_time = time.time()
        return round(elapsed / self.next_freq)

@dataclass
class LambdaGradualData:
    default_args: dict[str, ...]
    _calc: LambdaType

    def __post_init__(self):
        self.next_freq = 0
        self.start_time = time.time()

    def freq(self, args: dict) -> float:
        args.update(self.default_args)
        return self._calc(args)

    def gradual_spawn(self, condition: bool, args) -> int:
        # We need to reset time if the condition is false, so we decided that this would be a cleaner implementation
        if not condition:
            self.start_time = time.time()
            return 0 # Return 0 -> the consumer does not loop, thus no particles are spawned

        # If not enough time has passed, just exit
        elapsed = time.time() - self.start_time
        if elapsed < self.next_freq: return 0

        self.next_freq = uniform(self.freq(args), self.freq(args))
        self.start_time = time.time()
        return round(elapsed / self.next_freq)

def block_break_particles(manager: GameManager, loc: Location, ws: WorldSlices):
    spawn_range = (
        (loc.coords.x * BLOCK_SIZE, (loc.coords.x + 1) * BLOCK_SIZE),
        (loc.coords.y * BLOCK_SIZE, (loc.coords.y + 1) * BLOCK_SIZE)
    )

    for _ in range(randint(18, 26)):
        BlockParticle(manager, (randint(*spawn_range[0]), randint(*spawn_range[1])), loc[ws])

WALK_PC_DATA = GradualData((0.03, 0.12))
def walk_particles(manager: GameManager, loc: Location):
    if loc and not loc[WorldSlices.MIDDLEGROUND]: return
    player = manager.scene.player
    # "- sign(player.vel.x) * 8" to spawn the particles slightly behind the player
    # "- 2" to spawn the particles slightly above the ground so that they don't glitch into the ground
    spawn_pos = (player.rect.centerx - sign(player.vel.x) * 8, player.rect.bottom - 2)
    for _ in range(WALK_PC_DATA.gradual_spawn(abs(player.vel.x) > player.speed * 0.5)):
        BlockParticle(manager, spawn_pos, loc[WorldSlices.MIDDLEGROUND], Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE // 4))

def fall_particles(manager: GameManager, fall_dist: int, loc: Location):
    player = manager.scene.player
    # If the amount of particles spawned is higher than 16, clamp it to 16
    spawn_amount = (lower_bound := clamp_max(fall_dist, 16)[0], lower_bound + 3)
    # "- 2" to spawn the particles slightly above the ground so that they don't glitch into the ground
    spawn_pos = (player.rect.centerx, player.rect.bottom - 2)
    # Range of possible velocities, x and y
    spawn_vel_range = ((-4, 4), (-7, 2))
    for _ in range(randint(*spawn_amount)):
        BlockParticle(manager, spawn_pos, loc[WorldSlices.MIDDLEGROUND], Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE // 4), spawn_vel_range)

VOID_FOG_DATA = LambdaGradualData({"max_freq": 0.0027}, lambda args: args["max_freq"] + args["perc"] * 0.02)
def void_fog_particles(manager: GameManager) -> None:
    player_y = manager.scene.player.coords.y
    perc = (MAX_Y - player_y) / (MAX_Y / 8)

    offset = VEC(randint(0, SCR_DIM[0]), randint(0, SCR_DIM[1]))
    pos = manager.scene.player.camera.pos + offset

    image = Surface((20, 20))
    image.fill((70, 70, 70))

    for _ in range(VOID_FOG_DATA.gradual_spawn(True, {"perc": perc})):
        AtmosphericParticle(manager, pos, image)