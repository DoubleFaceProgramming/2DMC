# Version 0.2.0

## Additions

- Caves! Generated with Perlin Noise

## Changes

- Crosshair now fades between colors instead of instantly changing
- Added "Block position" to the debug menu, which shows the coordinates of the block the cursor is hovering over
- Added "Particles" to the debug menu, which shows the number of particles that is being calculated

## Bug fixes

- Fixed floating tall grass on chunk borders
- Particles float upwards when inside a block, now they just fall out

## Technical changes

- Grouped code into different files in the "src" folder
- Added comments, docstrings and type annotations explaining the code
- Separated collision detection from camera because that is just very bad
- Improved particle performance
