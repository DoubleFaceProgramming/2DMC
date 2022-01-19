from pygame import Surface

from src.constants import MAX_Y, BLUE_SKY

class Background():
    """Container class for drawing the background (sky)"""

    def __init__(self) -> None:
        self.sky = Background.Sky()
        self.cloud = self.sky.Cloud()
        self.sun = self.sky.Sun()
        self.moon = self.sky.Moon()

    def update(self, player_y: int) -> None:
        self.sky.update(player_y)
        # self.cloud.update()
        # self.sun.update()
        # self.moon.update()

    def draw(self, screen: Surface) -> None:
        self.sky.draw(screen)
        # self.cloud.draw()
        # self.sun.draw()
        # self.moon.draw()

    class Sky():
        """Class that handles the sky and all its sub-parts"""

        def __init__(self) -> None:
            self.color = (0, 0, 0)

        def update(self, player_y: int) -> None:
            # Fancy math algorithm to do some gradient shmuck
            # Blue at y = 0+, black at y = 1024-, and some colour changing in between
            # Trevor doesnt understand the maff so wont comment it but it looks cool
            # Also wk it shouldn't be a 1-liner but it looks so cool you can't not :D
            self.color = color if min((color := ([old + (new - old) * ((3.2 * (y_perc := player_y / MAX_Y) ** 3 - 6.16 * y_perc ** 2 + 4.13 * y_perc) / 1.17) for old, new in zip(BLUE_SKY, (0, 0, 0))]) if player_y > 0 else BLUE_SKY)) > 0 else (0, 0, 0)

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