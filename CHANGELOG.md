# Version 0.2.1

0.2.1 is a minor update following 0.2.0 that focuses more on bug fixes, optimizations, code improvements, and expandability changes.

---

## Additions

### Screenshot

- Press F2 to screenshot
- The screenshot image will be stored in a folder named "screenshots" in the same directory as main.py
- The image will be the same resolution as the resolution of the game (1200 x 600)

### Cinematic Modes

- To toggle cinematic modes, press F3
- There are 4 option to toggle through in order:
  - Show both the hotbar and crosshair
  - Hide both
  - Show crosshair but hide hotbar
  - Show hotbar but hide crosshair

### Hand Held Blocks

- Blocks will now physically appear in the player's hand when the player is holding an item

## Changes

- Optimized particles with conditional collision testing
- Text boxes now show their outer border / rect whilst in debug mode
- Velocity now shows up as BPS (blocks per second) in debug

## Bug Fixes

- Fixed particles occasionally falling into solid blocks
- Fixed void fog particles spawning in extremely large numbers when the player enters the upper threshold of void fog particles
- Fixed player being able to tunnel through blocks as FPS gets extremely low
- Fixed player tunnelling when the window is moved, now, the game will just pause with dt being set to 0

## Technical Changes

- Reworked the sprite system to allow better control over draw order, and to make the sprites easier to work with!
  - We now have a custom defined sprite class
    - This sprite class serves as a superclass for all other sprites, and provides a constructor and a number of methods that make all sprites compatible with our SpriteManager
  - We have a SpriteManager class that manages draw order, updates and other useful management functions
  - Draw order is defined in an automatic enumeration
  - Sprites can have a custom debug layer (debug information is rendered on a different layer to the sprite) or a regular debug layer (debug information is rendered on the same layer as the sprite)
  - If you want to get a better understanding of this system then you are best off looking at the code (particuarly [sprite.py](src/sprite.py)), be warned the code is kinda gross >.<
- Made a [text box class](src/text_box.py) to better how text boxes are handled. Text boxes are sprites, and so can be given different layers
- Velocity is now set and calculated with BPS (blocks per second)
