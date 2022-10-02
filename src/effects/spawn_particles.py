from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING: # Type annotations without causing circular imports
    from src.management.game_manager import GameManager
    from src.common.utils import WorldSlices
    from src.world.block import Location

from random import randint, uniform
from dataclasses import dataclass
from pygame import Rect
import time

from src.common.utils import to_pps, WorldSlices, sign
from src.effects.particles import BlockParticle
from src.common.constants import BLOCK_SIZE
from src.common.clamps import clamp_max

@dataclass
class GradualData:
    _freq_raw: tuple[float, float] | float

    def __post_init__(self):
        self.start_time = time.time()

    @property
    def freq(self):
        if isinstance(self._freq_raw, float):
            return (self._freq_raw, self._freq_raw)
        return self._freq_raw

    def gradual_spawn(self, condition: bool) -> bool:
        if not condition:
            self.start_time = time.time()
            return 0

        freq = uniform(*self.freq)
        elapsed = time.time() - self.start_time
        if elapsed < freq: return 0

        self.start_time = time.time()
        return round(elapsed / freq)

def block_break_particles(manager: GameManager, loc: Location, ws: WorldSlices):
    spawn_range = (
        (loc.coords.x * BLOCK_SIZE, (loc.coords.x + 1) * BLOCK_SIZE),
        (loc.coords.y * BLOCK_SIZE, (loc.coords.y + 1) * BLOCK_SIZE)
    )

    for _ in range(randint(18, 26)):
        BlockParticle(manager, (randint(*spawn_range[0]), randint(*spawn_range[1])), loc[ws])

WALK_PC_DATA = GradualData(0.1)
def walk_particles(manager: GameManager, loc: Location):
    if loc and not loc[WorldSlices.MIDDLEGROUND]: return
    player = manager.scene.player
    spawn_pos = (player.rect.centerx - sign(player.vel.x) * 8, player.rect.bottom - 2)
    for _ in range(WALK_PC_DATA.gradual_spawn(abs(player.vel.x) > player.speed * 0.5)):
        BlockParticle(manager, spawn_pos, loc[WorldSlices.MIDDLEGROUND], Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE // 4))

def fall_particles(manager: GameManager, fall_dist: int, loc: Location):
    player = manager.scene.player
    # If the amount of particles spawned is higher than 16, clamp it to 16
    spawn_amount = (lower_bound := clamp_max(fall_dist, 16)[0], lower_bound + 3)
    # "- sign(player.vel.x) * 8" to spawn the particles slightly behind the player
    # "- 2" to spawn the particles slightly above the ground so that they don't glitch into the ground
    spawn_pos = (player.rect.centerx - sign(player.vel.x) * 8, player.rect.bottom - 2)
    # Range of possible velocities, x and y
    spawn_vel_range = ((-4, 4), (-7, 2))
    for _ in range(randint(*spawn_amount)):
        BlockParticle(manager, spawn_pos, loc[WorldSlices.MIDDLEGROUND], Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE // 4), spawn_vel_range)