# 2DMC is a passion project to recreate the game "Minecraft" (all credit to Mojang Studios) in 2D.
# Copyright (C) 2022 Doubleface
# You can view the terms of the GPL License in LICENSE.md

# The majority of the game assets are properties of Mojang Studios,
# you can view their TOS here: https://account.mojang.com/documents/minecraft_eula

from pygame import Surface

from src.sprite import Sprite, LayersEnum
from src.constants import MAX_Y, BLUE_SKY
from src.particle import VoidFogParticle
from src.player import Camera
from src.block import Block

class Background(Sprite):
    """Container class for drawing the background (sky)"""

    def __init__(self, layer: LayersEnum = LayersEnum.BACKGROUND) -> None:
        super().__init__(layer)
        self.sky = Background.Sky()
        self.cloud = self.sky.Cloud()
        self.sun = self.sky.Sun()
        self.moon = self.sky.Moon()

    def update(self, dt: float, **kwargs) -> None:
        self.sky.update(kwargs["player_y"])
        self.cloud.update()
        self.sun.update()
        self.moon.update()

        VoidFogParticle.spawn(kwargs["camera"].pos, Block.instances, kwargs["player_y"])

    def draw(self, screen: Surface, **kwargs) -> None:
        self.sky.draw(screen)
        self.cloud.draw()
        self.sun.draw()
        self.moon.draw()

    class Sky():
        """Class that handles the sky and all its sub-parts"""

        def __init__(self) -> None:
            # The dimness of the sky is determined by a cubic relation between the player y-coords and the color multiplier
            # The values of the cubic function is approximated by a curve fitting website, see CREDITS.md
            # It is then slightly modified for our needs
            self.color_formula = lambda player_y: ((3.2 * (y_perc := player_y / MAX_Y) ** 3 - 6.16 * y_perc ** 2 + 4.13 * y_perc) / 1.17)
            self.old_player_y = 0 # Allows for a very minor optimsation
            self.color = (0, 0, 0)

        def update(self, player_y: int) -> None:
            if player_y != self.old_player_y:
                # Updating colour attribute using the above lambda
                self.color = color if min((color := ([old + (new - old) * self.color_formula(player_y) for old, new in zip(BLUE_SKY, (0, 0, 0))]) if player_y > 0 else BLUE_SKY)) > 0 else (0, 0, 0)
                self.old_player_y = player_y

        def draw(self, screen: Surface) -> None:
            """Clears the frame"""
            screen.fill(self.color)

        class Cloud():
            """Class that generates and handles clouds in the sky"""

            instances = []

            def __init__(self) -> None:
                # Placeholder classes and methods to be filled in at a later update
                pass

            def update(self) -> None:
                # Placeholder classes and methods to be filled in at a later update
                pass

            def draw(self) -> None:
                # Placeholder classes and methods to be filled in at a later update
                pass

        class Sun():
            """The class that updates and draws the sun"""

            def __init__(self) -> None:
                # Placeholder classes and methods to be filled in at a later update
                pass

            def update(self) -> None:
                # Placeholder classes and methods to be filled in at a later update
                pass

            def draw(self) -> None:
                # Placeholder classes and methods to be filled in at a later update
                pass

        class Moon(Sun):
            """The class that updates and draws the moon"""

            def __init__(self) -> None:
                # Placeholder classes and methods to be filled in at a later update
                pass

            def update(self) -> None:
                # Placeholder classes and methods to be filled in at a later update
                pass

            def draw(self) -> None:
                # Placeholder classes and methods to be filled in at a later update
                pass