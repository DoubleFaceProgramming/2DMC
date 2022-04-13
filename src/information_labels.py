# 2DMC is a passion project to recreate the game "Minecraft" (all credit to Mojang Studios) in 2D.
# Copyright (C) 2022 Doubleface
# You can view the terms of the GPL License in LICENSE.md

# The majority of the game assets are properties of Mojang Studios,
# you can view their TOS here: https://account.mojang.com/documents/minecraft_eula

from pygame.draw import rect as drawrect
from pygame.locals import SRCALPHA
from pygame import Rect, Surface
import time

from src.utils import smol_text, ultra_smol_text, SingleInstance
from src.sprite import LayersEnum, Sprite
from src.constants import VEC, WIDTH, Anchors

class InformationLabel(Sprite):
    """A non-functional base class for text boxes. Used only for inheritance"""

    def __init__(self, layer: LayersEnum, text: str, pos: tuple[int, int], survive_time: float | None = None, anchor: Anchors = Anchors.TOPLEFT) -> None:
        super().__init__(layer)

        # Text attributes
        self.text = text
        self.text_surf = smol_text(self.text)
        self.text_rect = self.text_surf.get_rect()

        # Size and positions attributes (size is slightly bigger than the text)
        self.anchor = VEC(anchor.value)
        self.size = VEC(self.text_rect.width + 16, self.text_rect.height + 8)
        self.pos = VEC(pos) - VEC((self.anchor.x + 1) * self.size.x, (self.anchor.y + 1) * self.size.y) // 2

        # Time attributes
        self.survive_time = survive_time
        self.start_time = time.time()

        # Creating an image with full opacity
        self.opacity = 255
        self.image = Surface(self.size, SRCALPHA)
        self.image.set_alpha(self.opacity)

        self.image.blit(self.text_surf, (8, 4))
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos

    def update(self, dt: float, **kwargs):
        self.rect.topleft = self.pos
        if self.survive_time: # If the text box shouldnt last for an infite time
            if (time_elapsed := time.time() - self.start_time) < self.survive_time:
                # Change the opacity based on the text box's lifetime
                self.opacity = 255 * (self.survive_time - time_elapsed) if time_elapsed > self.survive_time * 2/3 else 255
                self.image.set_alpha(self.opacity)
            else: # If the text box has lived longer than the survive time, kill it
                super().kill()

    def draw(self, screen: Surface, **kwargs) -> None:
        screen.blit(self.image, self.rect)

    def debug(self, screen, **kwargs) -> None:
        if self.survive_time:
            debug_text = ultra_smol_text(f"Time elapsed: {time.time() - self.start_time:.2f}") # Rounding the time to 2 decimal places
            debug_text.set_alpha(self.opacity)
            rect = Rect(self.rect.left, self.rect.top - self.rect.height / 2, debug_text.get_width(), debug_text.get_height())
            rect.centerx = self.rect.centerx # Centering the text
            screen.blit(debug_text, rect)

        drawrect(screen, (255, 0, 0), self.rect, width=1) # Drawing an outline rect

class GenericTextBox(InformationLabel, SingleInstance):
    """Text Box with a Minecraft-y magenta border that only supports one instance"""

    def __init__(self, layer: LayersEnum, text: str, pos: tuple[int, int], survive_time: float | None = None, anchor: Anchors = Anchors.TOPLEFT) -> None:
        InformationLabel.__init__(self, layer, text, pos, survive_time, anchor)
        SingleInstance.__init__(self, self)

        # Drawing a magenta border to give it a minecraft-y feel and blit the text on
        drawrect(self.image, (0, 0, 0), (2, 0, self.text_rect.width + 12, self.text_rect.height + 8))
        drawrect(self.image, (0, 0, 0), (0, 2, self.text_rect.width + 16, self.text_rect.height + 4))
        drawrect(self.image, (44, 8, 99), (2, 2, self.text_rect.width + 12, 2))
        drawrect(self.image, (44, 8, 99), (2, 4 + self.text_rect.height, self.text_rect.width + 12, 2))
        drawrect(self.image, (44, 8, 99), (2, 2, 2, self.text_rect.height + 4))
        drawrect(self.image, (44, 8, 99), (12 + self.text_rect.width, 2, 2, self.text_rect.height + 4))
        self.image.blit(self.text_surf, (8, 4)) # Reblitting text because it would get covered up by the border ^^

class HUDToast(GenericTextBox):
    def __init__(self, text: str) -> None:
        super().__init__(LayersEnum.TOASTS, text, (WIDTH - 10, 10), 3, Anchors.TOPRIGHT)

class InventoryLabel(GenericTextBox):
    """Text box class that simplifies inventory label management"""

    def __init__(self, text: str, pos: tuple[int, int]) -> None:
        super().__init__(LayersEnum.INVENTORY_LABELS, text, pos, survive_time=None)

    def update(self, dt: float, **kwargs):
        self.pos = (kwargs["mpos"][0] + 12, kwargs["mpos"][1] - 24) # Update position so label is always to the topleft of cursor
        super().update(dt, **kwargs)

class HotbarLabel(GenericTextBox):
    """Text box class that simplifies hotbar label management"""

    def __init__(self, text: str, pos: tuple[int, int]) -> None:
        super().__init__(LayersEnum.HOTBAR_LABELS, text, pos, survive_time=3)