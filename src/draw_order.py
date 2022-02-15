from enum import Enum, auto
from pygame import Surface
from typing import Any

class LayersEnum(Enum):
    BLOCK_SELECTION = auto()
    DEBUG = auto()
    PLAYER = auto()
    INVENTORY = auto()
    CROSSHAIR = auto()

class NoLayerAttributeException(Exception):
    def __init__(self, sprite: Any) -> None:
        self.sprite = sprite

    def __str__(self) -> str:
        return f"Class {self.sprite.__class__} does not have a layer attribute!"

    def __repr__(self) -> str:
        return f"Object {self.sprite} did not have a layer attribute."

class SpriteHandler:
    def __init__(self, *args: tuple[Any]) -> None:
        self.layers = {}
        if args:
            self.add(*args)

    def add(self, *args: tuple[Any]) -> None:
        for sprite in args:
            if not hasattr(sprite, "layer"):
                raise NoLayerAttributeException(sprite)

            if sprite.layer not in self.layers:
                self.layers[sprite.layer] = [sprite]
            else:
                self.layers[sprite.layer].append(sprite)

    def draw(self, screen: Surface, **kwargs) -> None:
        self.layers = dict(sorted(self.layers.items()))
        for layer in self.layers.values():
            for sprite in layer:
                sprite.draw(screen, kwargs)