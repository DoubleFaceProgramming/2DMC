# Contributing

This file will be filled in with all of our standards ect when we can be bothered.a
Until then this is basiocally a dumping ground for design docs :P

NOTE:
Add information on:

- Gamemanager
- Scenes
- Sprites + spritemanager
- Locations, blocks and chunks
- File strucure and root files
- Our modules
- Stuff in utils
- Styling conventions
- Anything else we deem useful
- Profiling + how to use it
- Inheritance trees (entities, particles, ect.)
- File formats (.structure, distribution.structure)

## World data design doc

Location:
(coords) -> Location -> Blocks
Chunks:
(chunk coords) -> Chunk -> Block data
Block Data:
(in-chunk coords) -> Reference to location (-> Blocks)
Block:
Block data - no references

To update:
Loop through every location, then through every block, then update the block
Loop through every chunk, then generate a surface that contains every location's blitted texture
-> Also generate a surface that contains every chunk if debug was activated (this surface would only have the debug information, not the block information. You would blit both textures)
To Draw (or debug):
Loop through every chunk and draw it
-> If debug, draw normally, then draw the debug surf above it.

Only chunks are sprites, and are the only ones called by the spritemanager.

## Licensing

As of version 0.2.1, 2DMC is licensed using the GNU General Public License v3. To comply with the license, all source files (ie. any code file within src/) contain the following header:

```Plaintext
2DMC is a passion project to recreate the game "Minecraft" (all credit to Mojang Studios) in 2D.
Copyright (C) 2022 Doubleface
You can view the terms of the GPL License in LICENSE.md

The majority of the game assets are properties of Mojang Studios,
you can view their TOS here: https://account.mojang.com/documents/minecraft_eula
```

The [main.py file](main.py) contains a slightly longer header which we have omitted for brevity.
You can view a full copy of the license in [LICENSE](LICENSE) OR [here](https://www.gnu.org/licenses/gpl-3.0.en.html)

## Sprites + Spritemanager

### Reasoning

In older versions of 2dmc we had a master list for every type of drawable "sprite" (particles, chunks, ect)
When we wanted to draw, we would some code similar to the following:

```python
for sprite in a_list_of_sprites:
    sprite.draw()
```

One issue we encountered whilst developing with this system was that we often needed sprites of the same kind to be drawn above / behind each other.
This isnt easily doable with the previous system, which led to a lot of janky code with singlular sprites being assigned to variables and lots of weird if checks and it was basically a massive mess.
We also had the issue where if we wanted to reorder the way sprites were drawn we would have tomanually go through and change the position of every related draw call.
No good.

So whilst developing v0.2.1 decided a new system was in order: the sprite system.

### Sprites

We have a sprite superclass that all sprites inherit from. This provides a common interface for conventional methods like `draw()`, `update()`, `debug()` and `kill()` and conventional attributes like `._layer`, `._debug_layer` and `.manager`
Every sprite class takes 2* mandatory argument, a manager (GameManager) and a layer (type: LayersEnum or int). It also takes one optional argument, debug_layer (same type)
If either the layer or the debug_layer is of type `LayerEnum` it will be converted to an `int` on initialisation.
Upon initalisation, the sprite will be added to a spritemanager.

\* The manager argument was added during the development of 0.3.0

The aforementioned LayersEnum is a python enum (`enum.Enum`) in which every argument is automatic (`enum.auto()`)
It represents the order in which sprites will be drawn. It means the orders can be redordered incredibly easy, and adding new orders is similarly very simple.

Every sprite that was given a layer in `__init__` will be drawn in the same layer, along with every other sprite given the same layer.
Layers and their corresponding sprites are drawn in the order of appearance in the LayersEnum enum.

A brief overview of all Sprite methods:

- `__init__(self, manager: GameManager, layer: int | LayersEnum, debug_layer: int | LayersEnum | None = None) -> None`
  - Initialise the sprite
- `draw(self) -> None`
  - Draw the sprite to the screen
- `update(self) -> None`
  - Update or change any class attributes, and handle class logic
- `debug(self) -> None`
  - Draw any debug information related to the sprite to the screen
- `kill(self) -> None`
  - Kill the sprite and handle any cleanup logic

\* Before the development of 0.3.0, the signitaures looked something more like:

- `__init__(self, layer: int | LayersEnum, debug_layer: int | LayersEnum | None = None) -> None`
- `draw(self, screen: pygame.Surface, **kwargs: dict[typing.Any]) -> None`
- `update(self, dt: float, **kwargs: dict[typing.Any]) -> None`
- `debug(self, screen: pygame.Surface, **kwargs: dict[typing.Any]) -> None`
- `kill(self) -> None`

To implement your own sprite, simply create a class that inherits from `Sprite` (v0.3.0+).
Make sure to call `super().__init__(manager, LayersEnum.THE_LAYER_YOU_WANT)`
Then just override any applicable methods to customise the behaviour of your new sprite.
Your sprite can also be killed with `sprite.kill()`
And you can also add the manager with `self.manager`, meaning you have access to pretty much every attribute in 2DMC. Neat!

### Spritemanager

This system doesnt work on its own, however.
The other half of the equation is the spritemanager class.

When initialised, spritemanager takes a manager (`GameManager`) and `*args` (`tuple[Sprite]`)
If any args are passed in they will be fed to `SpriteManager.add()`
A dictionary to hold layers is also created.

An explanation of SpriteManager's methods:

- `__iter__(self)` and `__next__`

    Makes SpriteManager an iterator so it can be... iterated over?
    The code and details of these functions are beyond the scope of this document (because the code is disgusting and unreadable)
    If, for some reason, you want to understand, modify or utilise this code in greater deal then you can find it [here](src/management/sprite.py)

- `__contains__(self, sprite: Sprite) -> bool`

    Adds support for python's `in` operator.
    It will check if the sprite is in its layer. I dont really know why it wouldnt be but its here... just in case.
    It will raise a SpriteNotFoundException if the sprite was not in it's layer.
    It will **print** a LayerNotFoundException if the sprite's layer was not in the spritemanager's layer dict.

- `add(self, *args: tuple[Sprite])`

    This method takes any number of sprites as an argument.
    It will add all these sprites to its layers dict, creating layers and debug layers as needed.
    See [Debug Layers](#debug-layers) for more information.

    It will raise a NoLayerAttributeException if the sprite does not have a ._layer attribute.

- `remove(self, sprite: Sprite)`

    This removes a sprite from its layer (+ debug layer if applicable)
    It will also delete the layer / debug layer if it is empty. This prevents a crash involving empty dicts.
    It will raise a SpriteNotFoundException if the sprite was not in it's layer.
    It will raise a LayerNotFoundException if the sprite's layer was not in the spritemanager's layer dict.

- `draw(self)`

    This function serves as both draw() and debug().
    We loop through every layer and every sprite.
    Then if the layer is not a debug layer we draw it.
    We also check if debug is active, if it is we check if the layer is a debug layer or if the sprite's debug layer is the same as its regular layer, in which case we will call `sprite.debug()`. For an explanation on why this is, see [Debug Layers](#debug-layers).

- `update(self)`

    We just loop through every sprite and update it, no trickery here :)

### Debug Layers

This is a feature I (Trevor) implemented because I thought having it not implemented would break the spirit and the point of the system. I now realise that we will likely never use this feature. It took a long time to write..

..oh well...

A debug layer is a layer whose name ends in `_DEBUG`.
If you pass `LayersEnum.NAME_DEBUG` or its value (`int`) into a sprite's `debug_layer: int | LayersEnum`, whenever debug is active, that sprite's debug information will be drawn on that layer.
If a sprite's `debug_layer` is not set then it's debug information will be drawn on its normal `layer`.
This makes the system (by my metrics) *entirely* customisable, which in my opinion is sort of worth it.
(even if we never use it :P)

### Exceptions

There are a few exceptions to make working with errors in this system easier.
They all implement from Exception.
The text following "Takes:" are the arguments to `__init__`.
The text following "Prints:" is whats returned from `__str__` (in pseudocode)
They are as follows:

- `NoLayerAttributeException`
    Takes: `Sprite`
    Prints: "Class `self.sprite.__class__` does not have a \_layer / \_debug_layer attribute!"

- `LayerNotFoundException`
    Takes: `int | Sprite`
        -> (if a sprite is given it's `_layer` attribute will be used)
    Prints: "Layer `LayersEnum(int | Sprite._layer).name` does not exist in the layer list!"

- `SpriteNotFoundException`
    Takes: `Sprite`
    Prints: "Sprite object `Sprite` does not exist in the sprite list!"
