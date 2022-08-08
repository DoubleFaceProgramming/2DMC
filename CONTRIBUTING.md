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
