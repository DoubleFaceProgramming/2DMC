from pygame import Surface

from src.particle import VoidFogParticle, Particle, background_particles
from src.constants import MAX_Y, BLUE_SKY
from src.player import Camera
from src.block import Block

class Background():
    """Container class for drawing the background (sky)"""

    def __init__(self) -> None:
        self.sky = Background.Sky()
        self.cloud = self.sky.Cloud()
        self.sun = self.sky.Sun()
        self.moon = self.sky.Moon()

    def update(self, player_y: int, camera: Camera) -> None:
        self.sky.update(player_y)
        self.cloud.update()
        self.sun.update()
        self.moon.update()

        VoidFogParticle.spawn(camera.pos, Block.instances, player_y)

    def draw(self, screen: Surface, camera: Camera) -> None:
        self.sky.draw(screen)
        self.cloud.draw()
        self.sun.draw()
        self.moon.draw()

        for particle in Particle.instances:
            if issubclass(particle.__class__, background_particles):
                particle.draw(screen, camera)

    class Sky():
        """Class that handles the sky and all its sub-parts"""

        def __init__(self) -> None:
            # The dimness of the sky is determined by a cubic relation between the player y-coords and the color multiplier
            # The values of the cubic function is approximated by a curve fitting website, see CREDITS.md
            # It is then slightly modified for our needs
            self.calc_color = lambda player_y: ((3.2 * (y_perc := player_y / MAX_Y) ** 3 - 6.16 * y_perc ** 2 + 4.13 * y_perc) / 1.17)
            self.old_player_y = 0 # Allows for a very minor optimsation
            self.color = (0, 0, 0)

        def update(self, player_y: int) -> None:
            if player_y != self.old_player_y:
                # Updating colour attribute using the above lambda
                self.color = color if min((color := ([old + (new - old) * self.calc_color(player_y) for old, new in zip(BLUE_SKY, (0, 0, 0))]) if player_y > 0 else BLUE_SKY)) > 0 else (0, 0, 0)
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