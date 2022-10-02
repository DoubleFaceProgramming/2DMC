# Spritemanager

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
