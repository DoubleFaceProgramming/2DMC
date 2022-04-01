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
- The current cinematic mode state will be shown by a popup displayed on the top-right

### Hand Held Blocks

- Blocks will now physically appear in the player's hand when the player is holding an item

### 2DMC logo

- 2DMC now has... a logo! It will be shown on the top left corner of the game window and in Alt+Tab menu!
- You can see it below:

![logo](https://imgur.com/UNfSbHV.png)

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

- Velocity is now set and calculated with BPS (blocks per second)
- We have implemented a Single Instance Superclass. This class ensures any subclasses can only have 1 instance of themselves at a time.
  - This is useful, for example for the inventory labels, where whenever you move the mouse a new label will spawn. However, we only want one label to spawn at a time. Previously this required a very complicated and extremely ugly system of kill methods and class attributes and conditional checks which was, in short, [gross](https://github.com/DaNubCoding/2DMC/commit/21970ed4f93699bfecfa0e321f33f127ece247e4?diff=split#r70245084).
  - This system removes the need for this. Any sprite that inherits from SingleInstance and calls it's constructor will have this handled automatically
  - Demo (because the constructor is slightly confusing):

  ```python
  class Foo(Sprite, SingleInstance):
    def __init__(self, layer: int | LayersEnum) -> None:
      Sprite.__init__(self, layer)
      SingleInstance.__init__(self, self) # The second self call passes the instance to SingleInstance, the first is just a __init__ thing ¯\_(ツ)_/¯
  ```

- We have implemented a new system called "Information Labels"
  - These labels can be defined as "anything non-permanent that conveys information or any other content".
  - This includes images, popups, labels, toasts, ect.
  - Made a [information label class](src/information_label.py) to better how these labels are handled. Labels are considered sprites internally, and so can be given different layers
  - Labels are designed with OOP in mind. As of 0.2.1 the inheritance tree is as follows:

  ```InheritanceTree
  InformationLabel
  └── GenericTextBox
      ├── InventoryLabelTextBox
      └── HotbarLabelTextBox
  ```

  - NOTE: GenericTextBox also inherits from SingleInstance but this is hard to show on an inheritance tree.
