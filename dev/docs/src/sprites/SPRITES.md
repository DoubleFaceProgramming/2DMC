### Sprites

We have a sprite superclass that all sprites inherit from. This provides a common interface for conventional methods like `draw()`, `update()`, `debug()` and `kill()` and conventional attributes like `._layer`, `._debug_layer` and `.manager` Every sprite class takes 2* mandatory argument, a manager (GameManager) and a layer (type: LayersEnum or int). It also takes one optional argument, debug_layer (same type)
If either the layer or the debug_layer is of type `LayerEnum` it will be converted to an `int` on initialisation.
Upon initalisation, the sprite will be added to a spritemanager.

* The manager argument was added during the development of 0.3.0

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
* Before the development of 0.3.0, the signitaures looked something more like:

* 
- `__init__(self, layer: int | LayersEnum, debug_layer: int | LayersEnum | None = None) -> None`

- `draw(self, screen: pygame.Surface, **kwargs: dict[typing.Any]) -> None`

- `update(self, dt: float, **kwargs: dict[typing.Any]) -> None`

- `debug(self, screen: pygame.Surface, **kwargs: dict[typing.Any]) -> None`

- `kill(self) -> None`

To implement your own sprite, simply create a class that inherits from `Sprite` (v0.3.0+).
Make sure to call `super().__init__(manager, LayersEnum.THE_LAYER_YOU_WANT)` Then just override any applicable methods to customise the behaviour of your new sprite.
Your sprite can also be killed with `sprite.kill()` And you can also add the manager with `self.manager`, meaning you have access to pretty much every attribute in 2DMC. Neat!
