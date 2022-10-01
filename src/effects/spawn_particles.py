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

# cond = ...
# data = ...
# for _ in range(gradual_spawn(cond, data)):
#     ...
def gradual_spawn(condition: bool, data: GradualData) -> bool:
    if not condition:
        data.start_time = time.time()
        return 0

    freq = uniform(*data.freq)
    elapsed = time.time() - data.start_time
    if elapsed < freq: return 0

    data.start_time = time.time()
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
    if not loc[WorldSlices.MIDDLEGROUND]: return
    player = manager.scene.player
    for _ in range(gradual_spawn(abs(player.vel.x) > player.speed * 0.5, WALK_PC_DATA)):
        spawn_pos = (player.rect.centerx - sign(player.vel.x) * 8, player.rect.bottom - 2)
        BlockParticle(manager, spawn_pos, loc[WorldSlices.MIDDLEGROUND], Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE // 4))
