# Sprite System Guide

You can view the source code for this demonstration [here](https://github.com/DoubleFaceProgramming/2DMC/tree/41bfa7a9c638989d8cd970e750cc0f5502e32d57/dev/rescources/sprite-system-demo), or in `dev/rescources/spritesystemdemo` on the latest github branch. (note: if we changed the path in the latest branch, let us know!)

This guide will be written using the 0.2.1 sprite system. The system has changed slightly in 0.3.0, however the update and rewrite is not yet finished, so I will use the old system for the demo whilst we work on the new version. I will try to remember to update this section when 0.3.0 is released; if I havent then make a Github issue and I'll fix it :) 

I'll start by writing the demo the old way we used to do it, to demonstrate the advantadges of the sprite system, then rewrite them to fit with the new standard and hopefully better explain how to implement your own Sprite classes in the process.

Assume the following file structure:

```tree
demo/
├── main.py
├── README.py
├── lib/
│   └── sprite.py
└── images/
    └── [...]
```

`sprite.py` contains the same content as [the 2DMC sprite system file,](src/management/sprite.py) minus the LayersEnum which we will go over in more detail in just one second.

We'll start in main.py with some boilerplate which I'm sure you have seen many times before so I won't bother explaining it :P

```python
from pygame.math import Vector2 as VEC
import pygame

from pygame.locals import * # Dont do this normally! I'm only doing this for demonstration!

WIDTH, HEIGHT = SCR_DIM = (1200, 800)
SPEED = 500
FPS = 80

pygame.init()
screen = pygame.display.set_mode(SCR_DIM)
pygame.display.set_caption("Sprite System Demonstration")
clock = pygame.time.Clock()

running = True
while running:
    screen.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
```

Next we'll write a quick player class:

```python
class Player:
    def __init__(self, pos: VEC | tuple[int, int]) -> None:
        self.size = VEC(80, 80)
        self.pos = VEC(pos)
        self.vel = VEC(0, 0)

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        self.vel = VEC(0, 0)

        if keys[K_a]:
            self.vel.x -= SPEED
        if keys[K_d]:
            self.vel.x += SPEED
        if keys[K_w]:
            self.vel.y -= SPEED
        if keys[K_s]:
            self.vel.y += SPEED

        self.pos += self.vel * dt

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, (0, 0, 0), self.pos - (self.size / 2), self.size.x / 2)
```

..and a square class:

```python
class Square:
    instances = []

    def __init__(self, pos: tuple[int, int] | VEC, colour: tuple[int, int, int]):
        self.__class__.instances.append(self)

        self.size = VEC(100, 100)
        self.pos = VEC(pos)

        self.colour = colour

    def update(self) -> None:
        pass # While I could omit update() for this example, you rarely can in practise so I'll leave it here.

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.colour, pygame.Rect(*self.pos, *self.size))
```

Cool! We can create them like so:

```python
player = Player((200, 200))
for i, colour in enumerate(((255, 0, 0), (0, 255, 0), (0, 0, 255))):
    Square((400, 200 + i * 50), colour)
```

..then update and draw them in the main `while` loop:

```python
for square in Square.instances:
    square.update()

player.update(dt)

for square in Square.instances:
    square.draw(screen) # Whilst we could merge these 2 loops for this demo you rarely can in practice so I won't here.

player.draw(screen)
```

If we run the code now we should see it working as expected:

![The squares are now seperated, and have a magenta border around them](https://raw.githubusercontent.com/DoubleFaceProgramming/2DMC/41bfa7a9c638989d8cd970e750cc0f5502e32d57/dev/rescources/sprite-system-demo/images/test_3.png)

We can see that the player is drawn above the sqaures and the squares draw in the order that was declared.

However, what if we decide that we instead want the green square to draw above the others?

Lets try and implement this:

We will now have to initialise the squares like so:

```python
s_r = Square((400, 200), (255, 0, 0))
s_g = Square((400, 250), (0, 255, 0))
s_b = Square((400, 300), (0, 0, 255))
```

Then draw them like this:

```python
for square in Square.instances:
    if square is not s_g:
        square.draw(screen)
s_g.draw(screen)
```

![3 squares of varying colours overlapping in the order red -> green <- blue. A black circle is drawn above all 3](https://raw.githubusercontent.com/DoubleFaceProgramming/2DMC/41bfa7a9c638989d8cd970e750cc0f5502e32d57/dev/rescources/sprite-system-demo/images/test_2.png "Image 2")

As you can see, we got the expected result. However:

1) The code is messy and hard to follow

2) The more rules we add (say, the player gets drawn above green), the worse this will become

3) Re-ordering the way sprites are drawn is gets increasingly complex and difficult the more sprites there are and the more sprites there are with seperate rules

4) It's difficult to make define where 1 instance of a class will be drawn relative to other instances of the class

5) Creating and drawing lots of classes and their instances will end up in long, repeated calls to `x.draw(screen)`, `y.draw(screen)`, `z.draw(screen)`, ect

Let's rewrite this using the Sprite system!

First, lets populate LayersEnum:

```python
class LayersEnum(Enum):
    SQUARE = auto()
    PLAYER = auto()
```

Next, lets make Player and Square officially Sprites:

```python
class Player(Sprite):
    def __init__(self, pos: VEC | tuple[int, int]) -> None:
        super().__init__(LayersEnum.PLAYER)
        ...
```

```python
class Square(Sprite):
    def __init__(self, layer: LayersEnum | int, pos: tuple[int, int] | VEC, colour: tuple[int, int, int]):
        super().__init__(layer)
        ...

    def update(self, dt) -> None:
        pass # While I could omit update() for this example, you rarely can in practise so I'll leave it here.
```

..that's all that you need to change! Just make the class inherit from Sprite and call `super().__init__(layer)` in your class's constructor. 

A few things to note:

- Because we always know that `Player` will draw on the PLAYER layer, we don't need to pass `layer` into `__init__`, we can just pass it through directly.
  
  - However, because we might change what layer a `Square` draws on we do need to pass a layer argument in.

- In `Square.update` we need to pass in `dt` to satisfy the `Sprite.update` function signature. This is a limit with the way the 0.2.1 sprite system works that is mitigated in 0.3.0 with the Scene, GameManager and `self.game` architecture (there will likely be a section on this in this document, whenever one of us gets around to writing it :P)

- Finally, we use the `LayersEnum | int` type annotation to refer to a layer argument. This is because `Sprite.__init__` can recieve and parse either a LayersEnum or an int. If you want to understand this in greater depth you can check out the Sprite baseclass.

Then we can initialise our Squares and Player:

```python
Player((200, 200))
Square(LayersEnum.SQUARE, (400, 200), (255, 0, 0))
Square(LayersEnum.SQUARE, (400, 250), (0, 255, 0))
Square(LayersEnum.SQUARE, (400, 300), (0, 0, 255))
```

This will automagically add the sprites to the SpriteManager.

Finally, we can draw and update the sprites in the main loop:

```python
SPRITE_MANAGER.update(dt)
SPRITE_MANAGER.draw(screen, False)
```

This works as expected.

![](https://raw.githubusercontent.com/DoubleFaceProgramming/2DMC/41bfa7a9c638989d8cd970e750cc0f5502e32d57/dev/rescources/sprite-system-demo/images/test_3.png "Image 3")

Now lets implement the green square displaying above the others:

Its as simple as:

1) Adding a new entry in LayersEnum:
   
   ```python
   ```python
   class LayersEnum(Enum):
       SQUARE = auto()
       GREEN_SQUARE = auto()
       PLAYER = auto()
   ```

2) Updating the sprite creation call:
   
   ```python
   Square(LayersEnum.SQUARE, (400, 200), (255, 0, 0))
   Square(LayersEnum.GREEN_SQUARE, (400, 250), (0, 255, 0))
   Square(LayersEnum.SQUARE, (400, 300), (0, 0, 255))
   ```

And thats it! 

![The same as Image 2](https://raw.githubusercontent.com/DoubleFaceProgramming/2DMC/41bfa7a9c638989d8cd970e750cc0f5502e32d57/dev/rescources/sprite-system-demo/images/test_2.png "Image 2 (again)")

The result is exactly the same as it was before (emphasis on *exactly* because I'm using the same images as earlier but it does actually work xD), but this time more maintainable, scaleable and readable.

The final part of this demonstration is to display Debug Layers.

Lets start by adding a simple debug toggle and passing it into `SpriteManager.draw`:

```python
debug = False
running = True
while running:
    screen.fill((255, 255, 255))
    dt = clock.tick_busy_loop(FPS) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_F1:
                debug = not debug

    SPRITE_MANAGER.update(dt)
    SPRITE_MANAGER.draw(screen, debug)
    ...
```

Then lets give `Square` a simple debug function. We'll make it display their outline in.. purple. I'm also going to seperate out the squares to make it a little easier to understand.

```python
>> Square
def debug(self, screen: pygame.Surface) -> None:
    pygame.draw.rect(screen, (255, 0, 255), pygame.Rect(*self.pos, *self.size), width=5)

>> Global
Square(LayersEnum.SQUARE, (400, 210), (255, 0, 0))
Square(LayersEnum.GREEN_SQUARE, (400, 320), (0, 255, 0))
Square(LayersEnum.SQUARE, (400, 430), (0, 0, 255))
```

If we run this and enable debug, we see:

![The magenta borderes are drawn above the back circle](https://raw.githubusercontent.com/DoubleFaceProgramming/2DMC/41bfa7a9c638989d8cd970e750cc0f5502e32d57/dev/rescources/sprite-system-demo/images/test_3.png)

Perfect! We can see the sprites' debug information are drawn above the sprite, but below any other sprite. However, let's say we want to have the square's debug information drawn above the player. This is the purpose of debug layers.
This scenario is actually quite common. For example, you may want to view the positions of sprites drawn below other sprites, which would be impossible if the debug information is bound to the layer of the sprite. 

First, add some new entries to the LayersEnum:

```python
class LayersEnum(Enum):
    SQUARE = auto()
    GREEN_SQUARE = auto()
    PLAYER = auto()
    SQUARE_DEBUG = auto()
    GREEN_SQUARE_DEBUG = auto()
```

**IMPORTANT: A debug layer must end with "_DEBUG"!**

Next, let's modify `Square.__init__`:

```python
def __init__(self, layer: LayersEnum | int, debug_layer: LayersEnum | int, pos: tuple[int, int] | VEC, colour: tuple[int, int, int]):
    super().__init__(layer, debug_layer)
```

And finally edit the square instantiation:

```python
Square(LayersEnum.SQUARE, LayersEnum.SQUARE_DEBUG, (400, 210), (255, 0, 0))
Square(LayersEnum.GREEN_SQUARE, LayersEnum.GREEN_SQUARE_DEBUG, (400, 320), (0, 255, 0))
Square(LayersEnum.SQUARE, LayersEnum.SQUARE_DEBUG, (400, 430), (0, 0, 255))
```

Then when we run it:

![](https://raw.githubusercontent.com/DoubleFaceProgramming/2DMC/41bfa7a9c638989d8cd970e750cc0f5502e32d57/dev/rescources/sprite-system-demo/images/test_4.png)

Perfect! The debug information is being drawn above the player. 

Hopefully this demonstration has served as a guide on creating your own sprites, a better understanding of layers and a visual explanation of debug layers!
