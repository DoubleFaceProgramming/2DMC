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

---

## Changes

- Optimized particles with conditional collision testing

---

## Bug Fixes

- Fixed particles occasionally falling into solid blocks
- Fixed void fog particles spawning in extremely large numbers when the player enters the upper threshold of void fog particles

---

## Technical Changes

- Reworked sprite draw order using a system that works as the following:
  - Explanation here