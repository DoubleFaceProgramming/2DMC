from pygame.constants import K_0, K_1, K_9
from src.sprite import LayersEnum
from pygame import Surface
import pygame
import time

from src.images import inventory_img, BLOCK_TEXTURES, hotbar_img, hotbar_selection_img
from src.utils import inttup, create_text_box, smol_text, CyclicalList
from src.constants import WIDTH, HEIGHT, SCR_DIM, VEC
import src.constants as constants
from src.sprite import Sprite

class Item:
    """Micro-class that stores metadata about items."""

    def __init__(self, name):
        self.name = name
        self.count = 1
        self.nbt = {}
        # NOTE: Add -= and += support for item count decrement and increment

# class HeldItem(Item):

#     scale = 0.3
#     def __init__(self, id: str | Item) -> None:
#         super().__init__(name)
#         self.image = scale(BLOCK_TEXTURES[self.name], inttup((BLOCK_SIZE * self.__class__.scale, self.__class__.scale * 0.3)))

class InventoryFullException(Exception):
    def __init__(self, item: Item, message="The inventory was full when trying to add item: ") -> None:
        self.message = message
        self.item = item
        super().__init__()

    def __str__(self) -> str:
        return (self.message + self.item.name)

class Inventory(Sprite):
    """Class that updates and draws the inventory and manages its contents."""

    def __init__(self, player, layer: LayersEnum = LayersEnum.INVENTORY) -> None:
        super().__init__(layer)
        self.player = player
        self.slot_start = VEC(400, 302)
        self.slot_size = (40, 40)
        self.items = {}
        self.hotbar = Hotbar(self)
        self.visible = False
        self.selected = None
        self.hovering = None
        self.over_hotbar = False
        self.max_items = 36
        self.hover_surf = pygame.surface.Surface(self.slot_size, pygame.SRCALPHA)
        self.hover_surf.fill((255, 255, 255))
        self.hover_surf.set_alpha(100)
        self.transparent_background = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
        self.transparent_background.fill((0, 0, 0, 125))

    def __iadd__(self, other):
        self.add_item(other)
        return self

    def update(self, dt: float, **kwargs) -> None:
        m_state = kwargs["m_state"]
        if self.visible:
            mpos = VEC(pygame.mouse.get_pos())
            # Check if the mouse is within the inventory slots area
            in_inv_x = self.slot_start.x < mpos.x < self.slot_start.x+(self.slot_size[0]+5)*9
            over_inv = self.slot_start.y < mpos.y < self.slot_start.y+(self.slot_size[1]+5)*3 and in_inv_x

            # Check if the mouse is within the inventory hotbar slots area
            self.over_hotbar = 446 < mpos.y < 446+(self.slot_size[1]+5) and in_inv_x

            # Save the item that the mouse is currently hovering over
            if over_inv:
                self.hovering = inttup(((mpos.x-self.slot_start.x)//(self.slot_size[0]+5), (mpos.y-self.slot_start.y)//(self.slot_size[1]+5)+1))
            elif self.over_hotbar:
                self.hovering = inttup(((mpos.x-400)//(self.slot_size[0]+5), 0))
            else:
                self.hovering = None

            # If the mouse left button is pressed when it is hovering over a valid slot
            if m_state == 1 and (over_inv or self.over_hotbar):
                if self.hovering in self.items:                   # If the hovering slot has an item
                    if not self.selected:                         # If nothing is currently picked up
                        self.selected = self.items[self.hovering] # Pick up the item that is being hovered over
                        self.clear_slot(self.hovering)            # Remove the item in the slot
                    else:                                         # If something is already picked up
                        tmp = self.selected                       # Save the name of the item that is picked up
                        self.selected = self.items[self.hovering] # Set the picked up item to the one hovered over
                        self.set_slot(self.hovering, tmp.name)    # Set the hovered slot to the item that was saved
                else:                                                    # If the hovered slot is empty
                    if self.selected:                                    # If there is something that is picked up
                        self.set_slot(self.hovering, self.selected.name) # Set the hovered slot to be that item
                        self.selected = None                             # Empty whatever was picked up

        # If the scroll wheel is scrolled, pass that into the hotbar update, if not, pass in 0
        if m_state == 4 or m_state == 5:
            self.hotbar.update(m_state)
        else:
            self.hotbar.update(0)
        
        try:
            self.holding = self.hotbar.items[self.hotbar.selected]
        except KeyError:
            self.holding = None

    def draw(self, screen: Surface, **kwargs) -> None:
        self.hotbar.draw(screen)
        if self.visible:
            # Draw the dimming layer of background when the inventory opens up
            screen.blit(self.transparent_background, (0, 0))
            screen.blit(inventory_img, (VEC(SCR_DIM)/2-VEC(inventory_img.get_width()/2, inventory_img.get_height()/2)))

            # Display the item images in the correct slots
            for slot in self.items:
                item_img = pygame.transform.scale(BLOCK_TEXTURES[self.items[slot].name], self.slot_size)
                if slot[1]:
                    screen.blit(item_img, self.slot_start+VEC(slot[0]*(self.slot_size[0]+5), (slot[1]-1)*(self.slot_size[1]+5)))
                else:
                    screen.blit(item_img, self.slot_start+VEC(0, 190)+VEC(slot[0]*(self.slot_size[0]+5), (slot[1]-1)*(self.slot_size[1]+5)))

            # Drawing an slightly transparent selection / hovering rectangle behind the mouse cursor
            # We get the pos by adding the starting position of the inventory to a vector containing the slot the player is hovering over (hotbar
            # is classed as y0, so we set this to 4 if the user is over the hotbar so it displays correctly. We also -1 because... idk it justs makes it
            # work, and times it by the size of a slot + 5 because that is the distance between the left side of each slot, there is a 5px border), and
            # another vector that contains (0, 10) if the player is hovering over the hotbar and (0, 5) if not. This is because there is a 10px
            # between the inventory and the hotbar.
            if self.hovering:
                screen.blit(self.hover_surf, self.slot_start + ( VEC(self.hovering[0], (self.hovering[1] if not self.over_hotbar else 4) - 1) * (self.slot_size[0] + 5) ) + VEC((0, 10) if self.over_hotbar else (0, 0)))

            # Display the item that is picked up but slightly smaller by a factor of 0.9
            if self.selected:
                screen.blit(pygame.transform.scale(BLOCK_TEXTURES[self.selected.name], inttup(VEC(self.slot_size)*0.9)), VEC(pygame.mouse.get_pos())-VEC(self.slot_size)*0.45)

            # Draw the textbox of the item that is being hovered over
            if self.hovering in self.items:
                name = self.items[self.hovering].name.replace("_", " ").capitalize()
                mpos = pygame.mouse.get_pos()
                if self.selected == None:
                    surf, pos = create_text_box(smol_text(name), (mpos[0]+12, mpos[1]-24), 255)
                    screen.blit(surf, pos)

            # Draw the player paper doll in the inventory
            self.player.leg2.rect = self.player.leg2.image.get_rect(center=(593+self.player.width/2, 140+72))
            screen.blit(self.player.leg2.image, self.player.leg2.rect.topleft)
            self.player.arm2.rect = self.player.arm2.image.get_rect(center=(593+self.player.width/2, 140+35))
            screen.blit(self.player.arm2.image, self.player.arm2.rect.topleft)
            self.player.body.rect = self.player.body.image.get_rect(center=(593+self.player.width/2, 140+51))
            screen.blit(self.player.body.image, self.player.body.rect.topleft)
            self.player.arm.rect = self.player.arm.image.get_rect(center=(593+self.player.width/2, 140+35))
            screen.blit(self.player.arm.image, self.player.arm.rect.topleft)
            self.player.head.rect = self.player.head.image.get_rect(center=(593+self.player.width/2, 140+23))
            screen.blit(self.player.head.image, self.player.head.rect.topleft)
            self.player.leg.rect = self.player.leg.image.get_rect(center=(593+self.player.width/2, 140+72))
            screen.blit(self.player.leg.image, self.player.leg.rect.topleft)

    def set_slot(self, slot: int, item: str) -> None:
        """Set the given slot in the inventory to the given item

        Args:
            slot (int): The slot to set
            item (str): A string that contains the item name
        """

        self.items[slot] = Item(item)

    def clear_slot(self, slot: int) -> None:
        """Clear a slot in the inventory

        Args:
            slot (int): The slot to clear
        """

        del self.items[slot]

    def add_item(self, item: str | Item) -> None:
        """Append the item to the first empty slot

        Args:
            item (str): The name of the item to add

        Raises:
            InventoryFullException: Raised if there is no room in the inventory.
        """

        match item:
            case str(item):
                item = Item(item)
            case Item(item):
                pass # Sonarlint shut up!
            case _:
                raise TypeError("Item must be of type 'str' or 'Item'")

        for y in range(4):
            for x in range(9):
                if not (x, y) in self.items:
                    self.items[(x, y)] = item
                    return

        raise InventoryFullException(item)

class Hotbar:
    """Class that draws, updates and provides functionality for the hotbar."""

    def __init__(self, inventory: Inventory) -> None:
        self.slot_start = VEC(WIDTH / 2 - hotbar_img.get_width() / 2, HEIGHT - hotbar_img.get_height())
        self.slot_size = (40, 40)
        self.inventory = inventory
        items = {}
        for slot in self.inventory.items:
            if slot[1] == 0:
                items[slot[0]] = self.inventory.items[slot]
        self.items = items
        self.selected = 0
        self.fade_timer = 0
        self.scroll = self.HotbarScroll(self)

    def update(self, scroll: int) -> None:
        # Updating the hotbar with items from the inventory
        hotbar_items = {}
        for slot in self.inventory.items:
            if slot[1] == 0:
                hotbar_items[slot[0]] = self.inventory.items[slot]

        self.items = hotbar_items
        if not self.inventory.visible:
            keys = pygame.key.get_pressed()

            # Checking if the player has pressed a key within the range 1-9
            # range() is not inclusive so we +1 to the max bounds
            for num_key in range(K_1, K_9 + 1):
                if keys[num_key]:
                    self.change_selected(num_key - K_0 - 1) # Minusing the lowest bounds and 1 (because we +1-ed earlier)
                    self.fade_timer = time.time() # Resetting the fade timer

            # Increasing or decreasing scroll object (using a kinda unecessary but cool new feature :D)
            match scroll:
                case 4: self.scroll -= 1
                case 5: self.scroll += 1

            # If the user has scrolled, reset the fade time and update the scroll obj
            if scroll:
                self.fade_timer = time.time()
                self.scroll.update()

    def draw(self, screen: pygame.Surface) -> None:
        if not constants.MANAGER.cinematic.value["HB"]: return

        # Drawing the hotbar and selected "icon"
        screen.blit(hotbar_img, self.slot_start)
        screen.blit(hotbar_selection_img, (self.slot_start - VEC(2, 2) + VEC(self.slot_size[0] + 10, 0) * self.selected))

        # Drawing the item texture onto the hotbar slot
        for slot in self.items:
            item_img = pygame.transform.scale(BLOCK_TEXTURES[self.items[slot].name], self.slot_size)
            screen.blit(item_img, self.slot_start + VEC(8, 0) + VEC(slot * (self.slot_size[0] + 10), 8))

        # If it has been 3 seconds since self.fade_timer has been reset:
        if (time_elapsed := time.time() - self.fade_timer) < 3:
            if self.selected in self.items: # If you are holding an item
                opacity = 255 * (3-time_elapsed) if time_elapsed > 2 else 255 # Dims the opacity if it has been longer than 2 seconds
                # Generating text and a text box
                blitted_text = smol_text(self.items[self.selected].name.replace("_", " ").capitalize())
                surf, pos = create_text_box(blitted_text, (WIDTH / 2-blitted_text.get_width() / 2 - 8, HEIGHT - 92), opacity)
                screen.blit(surf, pos)

    def change_selected(self, new: int) -> None:
        """Change the selected slot

        Args:
            new (int): The new slot to select
        """

        self.scroll.current = new
        self.selected = new

    class HotbarScroll(CyclicalList):
        """Micro-class that allows for cyclical hotbar scrolling."""

        def __init__(self, hotbar, min: int = 0, max: int = 9) -> None:
            self.hotbar = hotbar
            super().__init__([*range(min, max)])

        def update(self) -> None:
            self.hotbar.selected = self.current