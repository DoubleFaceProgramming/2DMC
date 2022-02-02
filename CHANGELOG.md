# Version 0.2.0

## Additions

### New blocks

- Granite
- Diorite
- Andesite
- Coal ore
- Iron ore
- Gold ore
- Lapis ore
- Redstone ore
- Diamond ore
- Emerald ore
- Deepslate
- Cobbled deepslate
- Deepslate coal ore
- Deepslate iron ore
- Deepslate gold ore
- Deepslate lapis ore
- Deepslate redstone ore
- Deepslate diamond ore
- Deepslate emerald ore

### Caves

- Generated with Perlin Noise
- You will sometimes find grass and dirt getting cut off without any actual cave generating, that is a quirkiness in cave generation
- Caves will not be able to cut through bedrock

### Stone Types

- There are 4 new stone types:
  - Granite
  - Diorite
  - Andesite
  - Tuff
- Granite, diorite, and andesite generate anywhere above deepslate level ( < chunk-y 64)
- Tuff only generates below deepslate level ( > chunk-y 64)
- Their shapes are determined by a Cellular Automata algorithm
- They will not generate overlapping with ore veins, neither will they replace dirt, ores, nor bedrock

### Ore Veins

- Ore vein shapes are determined by a Cellular Automata algorithm.
- They will turn into deepslate variants of the ores if they generate replacing deepslate
- Ores will not replace bedrock or dirt

#### Distribution

- They generate underground with the following distribution (all percentages represent the chance of generation per chunk):
  - Coal ore (2 attempts per chunk) starts generating with a 16% chance at the top of the world, decreases until it reaches chunk-y 64, gets more common going down until chunk-y 96 with a 3% chance, then gets rarer until chunk-y 128
  - Iron ore (2 attempts per chunk) starts generating at the top of the world rarely, quickly goes to 10% chance at chunk-y 8, then gets rarer as chunk-y goes down to 72
  - Lapis ore (1 attempt per chunk) starts generating at chunk-y 32, gets more common until chunk-y 64 with a 6% chance, then gets rarer until chunk-y 96
  - Gold ore (1 attempt per chunk) starts generating at chunk-y 56, gets more common until chunk-y 88 with a 7% chance, then gets rarer until chunk-y 120
  - Redstone ore (2 attempts per chunk) starts generating at chunk-y 56, gets more common until chunk-y 120, then quickly gets rarer until chunk-y 128
  - Diamond ore (1 attempt per chunk) starts generating at chunk-y 56, maintains a 1% chance of generating until chunk-y 96, then gets more common until chunk-y 128 with a 5% chance
  - Emerald ore (1 attempt per chunk) starts generating at chunk-y 56, maintains a 1% chance of generating until chunk-y 72, then gets more common until chunk-y 96 with a 3% chance, then gets rarer until chunk-y 120

#### Best y-level for mining

- The best chunk-y to mine for each ore, the attempts per chunk, and the chance per attempt:
  - Coal: 2 (not 1 because a large portion of chunk-y 1 is made up of dirt), 16%, 2
  - Iron: 8, 10%, 2
  - Lapis: 64, 6%, 1
  - Gold: 88, 7%, 1
  - Redstone: 120, 15%, 2
  - Diamond: 126 (not 128 or 127 because a large portion of them are made up of bedrock), 5%, 1
  - Emerald: 96, 3%, 1

### Block Selection Box

- Added a selection box around the block that the crosshair is hovering over
- It is 2 pixels thick, and is offset towards the topleft corner by 2 pixels to fit the selected block entirely within the box

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
- Greatly improved chunk loading performance considering the new terrain features that have been added

### Profiling

- To make a profile for a function, pass the function into src.utils.profile, along with its parameters
- It will create a .prof file in build/profiles on the function that has been passed when F9 is pressed
- The file will have the time of creation in its file name
