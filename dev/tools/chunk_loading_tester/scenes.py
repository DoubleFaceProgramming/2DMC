from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_manager import GameManager

from sprite import SpriteManager

class Scene:
    def __init__(self, manager: GameManager) -> None:
        self.manager = manager
        self.start()

    def setup(self) -> None:
        self.sprite_manager = SpriteManager(self.manager)

    def update(self) -> None:
        self.sprite_manager.update()

    def draw(self) -> None:
        self.sprite_manager.draw()

    def kill(self) -> None:
        self.running = False

    def start(self) -> None:
        self.running = True