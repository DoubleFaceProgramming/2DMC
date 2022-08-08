# Contributing

This file will be filled in with all of our standards ect when we can be bothered.a
Until then this is basiocally a dumping ground for design docs :P

NOTE:
Add information on:

- Licensing
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
