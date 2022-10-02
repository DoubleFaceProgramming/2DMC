# Debug Layers

A debug layer allows a sprite to display its debug information on a different layer than the one its image is drawn on.

The layer name ends in `_DEBUG`.
If you pass `LayersEnum.NAME_DEBUG` or its value (`int`) into a sprite's `debug_layer: int | LayersEnum`, whenever manager.debug is active, that sprite's debug information will be drawn on that layer.
If a sprite's `debug_layer` is not set then its debug information will be drawn on its normal `layer`.
