# Version 0.2.0

## Additions

- Added caves! Generated with Perlin Noise
- Added ore veins. Their shapes are determined by a Cellular Automata algorithm. They generate underground with the following distribution:
  - Coal ore and iron ore generate anywhere underground
  - Gold ore generates below y40
  - Lapis lazuli ore generates below y56
  - Redstone ore generates below y80
  - Diamond ore generates below y128
  - Emerald ore generates below y160
- Added stone blobs. They generate everywhere underground, the shape is determined by a Cellular Automata algorithm
- Added a selection box around the block that the crosshair is hovering over

## Changes

- Crosshair now fades between colors instead of instantly changing
- The colour now has a gradient between the default blue (y = 0-) and black (y = 1024)
- Added "Block position" to the debug menu, which shows the coordinates of the block the crosshair is hovering over
- Added "Particles" to the debug menu, which shows the number of particles that is being calculated
- Added a transparent white overlay on the inventory slot that is being hovered over

## Bug fixes

- Fixed floating tall grass on chunk borders
- Particles float upwards when inside a block, now they just fall out
- Fixed tall grass being cut off by a tree on chunk borders

## Technical changes

- Grouped code into different files in the "src" folder
- Added comments, docstrings and type annotations explaining the code
- Separated collision detection from camera because that is just very bad
- Improved particle performance
- Greatly improved chunk loading performance