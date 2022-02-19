from __future__ import annotations

from enum import Enum, auto
from pygame import Surface
from typing import Any

class LayersEnum(Enum):
    BACKGROUND = auto()
    ENV_PARTICLES = auto()
    BLOCKS = auto()
    REG_PARTICLES = auto()
    BLOCK_SELECTION = auto()
    DEBUG = auto()
    PLAYER = auto()
    INVENTORY = auto()
    CROSSHAIR = auto()

class Sprite:
    def __init__(self, layer: int | LayersEnum) -> None:
        # In theory try except is faster as layer will almost always be an enum, so may as well
        try:
            self.layer = layer.value
        except AttributeError:
            if isinstance(layer, int):
                self.layer = layer
            else:
                raise TypeError("Argument 'layer' must be of type int or Enum item")

    def update(self, dt: float, **kwargs) -> None:
        return

    def draw(self, screen: Surface, **kwargs) -> None:
        return

    def debug(self, screen: Surface, **kwargs) -> None:
        return

    def kill(self) -> None:
        return

class NoLayerAttributeException(Exception):
    def __init__(self, sprite: Sprite) -> None:
        self.sprite = sprite

    def __str__(self) -> str:
        return f"Class {self.sprite.__class__} does not have a layer attribute!"

class LayerNotFoundException(Exception):
    def __init__(self, layer: int) -> None:
        self.layer = layer

    def __str__(self) -> str:
        return f"Layer {LayersEnum(self.layer).name} does not exist in the layer list!"

class SpriteNotFoundException(Exception):
    def __init__(self, sprite: Sprite) -> None:
        self.sprite = sprite

    def __str__(self) -> str:
        return f"Sprite object {self.sprite} does not exist in the sprite list!"

class SpriteHandler:
    def __init__(self, *args: tuple[Sprite]) -> None:
        self.layers = {}
        if args:
            self.add(*args)

    def __iter__(self) -> SpriteHandler:
        self.layers = dict(sorted(self.layers.items()))
        self.layeriter = self.spriteiter = 0
        return self

    def __next__(self) -> Sprite:
        if self.layeriter >= len(self.layers):
            raise StopIteration

        layer = list(self.layers.values())[self.layeriter]
        self.spriteiter += 1
        if self.spriteiter >= len(layer):
            self.layeriter += 1
            self.spriteiter = 0

        return layer[self.spriteiter] # bread

    def add(self, *args: tuple[Sprite]) -> None:
        for sprite in args:
            if not hasattr(sprite, "layer"):
                raise NoLayerAttributeException(sprite)

            if sprite.layer not in self.layers:
                self.layers[sprite.layer] = [sprite]
            else:
                self.layers[sprite.layer].append(sprite)

    def remove(self, sprite: Sprite) -> None:
        try:
            self.layers[sprite.layer].remove(sprite)
        except ValueError:
            if sprite.layer not in self.layers:
                raise LayerNotFoundException(sprite.layer)
            if sprite not in self.layers[sprite.layer]:
                raise SpriteNotFoundException(sprite)

        if not self.layers[sprite.layer]:
            del self.layers[sprite.layer]

    def draw(self, screen: Surface, **kwargs) -> None:
        for sprite in self:
            sprite.draw(screen, **kwargs)

    def update(self, dt: float, **kwargs) -> None:
        for sprite in self:
            sprite.update(dt, **kwargs)

    def debug(self, screen: Surface, **kwargs) -> None:
        for sprite in self:
            sprite.debug(screen, **kwargs)