# Exceptions

There are a few exceptions to make working with errors in this system easier.
They all implement from Exception.
The text following "Takes:" are the arguments to `__init__`.
The text following "Prints:" is whats returned from `__str__` (in pseudocode)
They are as follows:

- `NoLayerAttributeException` Takes: `Sprite` Prints: "Class `self.sprite.__class__` does not have a _layer / _debug_layer attribute!"

- `LayerNotFoundException` Takes: `int | Sprite`
  
  ```
    -> (if a sprite is given it's `_layer` attribute will be used)
  ```
  
  Prints: "Layer `LayersEnum(int | Sprite._layer).name` does not exist in the layer list!"

- `SpriteNotFoundException` Takes: `Sprite` Prints: "Sprite object `Sprite` does not exist in the sprite list!"
