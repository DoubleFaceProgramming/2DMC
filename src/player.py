from pygame.constants import K_a, K_d, K_w
from math import ceil, floor, degrees, radians, tan, cos, sin
from pygame import Surface, Rect
from pygame.math import Vector2
import pygame

from src.block import Block, BLOCK_DATA, remove_block, is_placeable, set_block, inttup
from src.constants import MAX_Y, SCR_DIM, GRAVITY, TERMINAL_VEL, CHUNK_SIZE, BLOCK_SIZE
from src.utils import block_collide, sign, text, pps
from src.particle import PlayerFallParticle
from src.sprite import LayersEnum, Sprite
from src.inventory import Inventory
import src.constants as constants
from src.images import *

class Camera(pygame.sprite.Sprite):
    """Class that represents the camera"""
    def __init__(self, player) -> None:
        self.player = player
        self.pos = self.player.size / 2
        self.pos = self.player.pos - self.pos - VEC(SCR_DIM) / 2 + self.player.size / 2

    def update(self, dt: float) -> None:
        mpos = pygame.mouse.get_pos()
        tick_offset = self.player.pos - self.pos - VEC(SCR_DIM) / 2 + self.player.size / 2
        if -1 < tick_offset.x < 1:
            tick_offset.x = 0
        if -1 < tick_offset.y < 1:
            tick_offset.y = 0
        if not self.player.inventory.visible:
            x_dist, y_dist = mpos[0] - SCR_DIM[0] / 2, mpos[1] - SCR_DIM[1] / 2
        else:
            x_dist, y_dist = 0, 0
        dist_squared = VEC(sign(x_dist) * x_dist ** 2 * 0.6, sign(y_dist) * y_dist ** 2 * 1.2)

        self.pos += (tick_offset * 2 + VEC(dist_squared) / 300) * dt

class Player(Sprite):
    """Class that contains player methods and attributes."""
    def __init__(self, layer: LayersEnum = LayersEnum.PLAYER) -> None:
        super().__init__(layer)
        self.size = VEC(0.225 * BLOCK_SIZE, 1.8 * BLOCK_SIZE)
        self.width, self.height = self.size.x, self.size.y
        self.start_pos = VEC(0, 1000) * BLOCK_SIZE # Far lands: 9007199254740993 (aka 2^53)
        self.pos = VEC(self.start_pos)
        self.coords = self.last_standing_coords = self.pos // BLOCK_SIZE
        self.slide = pps(20)
        self.acc = VEC(0, 0)
        self.vel = VEC(0, 0)
        # Minecraft:
        # Walking speed: 4.317 BPS
        # Sprinting speed: 5.612 BPS
        # Sprint-jumping speed: 7.127 BPS
        self.max_speed = pps(4.317)
        self.jumping_max_speed = pps(5.612)
        self.jump_vel = pps(-8.4)
        self.rect = pygame.Rect((0, 0, 0.225 * BLOCK_SIZE, 1.8 * BLOCK_SIZE))
        self.bottom_bar = pygame.Rect((self.rect.x + 1, self.rect.bottom), (self.width - 2, 1))
        self.on_ground = False
        self.direction = "right"

        self.head, self.body, self.leg, self.leg2, self.arm, self.arm2 = [pygame.sprite.Sprite() for _ in range(6)]
        self.head.image, self.body.image, self.leg.image = player_head, player_body, player_leg
        self.leg2.image, self.arm.image, self.arm2.image = player_leg, player_arm, player_arm
        self.head.rect, self.body.rect = self.head.image.get_rect(), self.body.image.get_rect()
        self.leg.rect, self.leg2.rect = self.leg.image.get_rect(), self.leg2.image.get_rect()
        self.arm.rect, self.arm2.rect = self.arm.image.get_rect(), self.arm2.image.get_rect()
        self.head.rot = 0
        self.leg.count = 0
        self.leg.rot = 0
        self.leg2.rot = 0
        self.arm.rot = 0
        self.arm2.rot = 0

        self.camera = Camera(self)
        self.inventory = Inventory(self)
        self.crosshair = Crosshair(self, 1750)

        self.inventory += "grass_block"
        self.inventory += "dirt"
        self.inventory += "stone"
        self.inventory += "grass"
        self.inventory += "oak_log"
        self.inventory += "oak_leaves"
        self.inventory += "oak_planks"
        self.inventory += "cobblestone"
        self.inventory += "glass"
        self.inventory += "poppy"
        self.inventory += "dandelion"
        self.inventory += "tall_grass"
        self.inventory += "granite"
        self.inventory += "diorite"
        self.inventory += "andesite"
        self.inventory += "coal_ore"
        self.inventory += "iron_ore"
        self.inventory += "gold_ore"
        self.inventory += "lapis_ore"
        self.inventory += "redstone_ore"
        self.inventory += "diamond_ore"
        self.inventory += "emerald_ore"
        self.inventory += "deepslate"
        self.inventory += "cobbled_deepslate"
        self.inventory += "deepslate_coal_ore"
        self.inventory += "deepslate_iron_ore"
        self.inventory += "deepslate_gold_ore"
        self.inventory += "deepslate_lapis_ore"
        self.inventory += "deepslate_redstone_ore"
        self.inventory += "deepslate_diamond_ore"
        self.inventory += "deepslate_emerald_ore"
        self.inventory += "tuff"

    def update(self, dt: float, **kwargs) -> None:
        self.camera.update(dt)

        keys = pygame.key.get_pressed()
        # Calculate player's velocity with a little bit of slipperiness
        if keys[K_a] and not self.inventory.visible:
            if self.vel.x > -self.max_speed:
                # Slow the player down
                self.vel.x -= self.slide * dt
        elif self.vel.x < 0:
            self.vel.x += self.slide * dt
        if keys[K_d] and not self.inventory.visible:
            if self.vel.x < self.max_speed:
                # Slow the player down but in the other direction
                self.vel.x += self.slide * dt
        elif self.vel.x > 0:
            self.vel.x -= self.slide * dt
        # If the player is on the ground and not in the inventory, jump
        if keys[K_w] and self.on_ground and not self.inventory.visible:
            self.vel.y = self.jump_vel
            # When the player jumps, its x-speed also increases slightly (aka sprint jumping in minecraft)
            self.vel.x *= 1.133
            # Accelerate the player unless its speed is already at the maximum
            if self.vel.x > self.jumping_max_speed:
                self.vel.x = self.jumping_max_speed
            elif self.vel.x < -self.jumping_max_speed:
                self.vel.x = -self.jumping_max_speed
        if -self.slide * dt < self.vel.x < self.slide * dt:
            self.vel.x = 0

        # Accelerate the player downwards
        self.acc.y = pps(GRAVITY)
        self.vel += self.acc * dt
        # Unless the player has reached terminal velocity
        if self.vel.y > pps(TERMINAL_VEL):
            self.vel.y = pps(TERMINAL_VEL)
        # Slow the player down if the player walking on the ground
        if self.on_ground:
            self.vel.x += -sign(self.vel.x) * pps(1) * dt

        # Move the test for collision
        self.move(kwargs["blocks"], dt)

        # Check if the player is on the ground with a bar at the bottom of the player
        for block in self.detecting_blocks:
            if self.bottom_bar.colliderect(block.rect):
                self.on_ground = True

                # Calculate the fall distance, how many blocks the player fell
                # If the player fell for more than or equal to 4 blocks
                if (fall_dist := abs(int((self.last_standing_coords - self.coords).y))) >= 4:
                    # The amount of particles to generate, an upper bound and a lower bound
                    amount = (lower_bound := (excess_vel // 2 if (excess_vel := fall_dist - 4 + 6) < 15 else 15), lower_bound + 3)
                    PlayerFallParticle.spawn(inttup(block.coords - VEC(0, 1)), Block.instances, block, amount)
                # Update the last standing coords used to calculate the fall distance
                self.last_standing_coords = self.coords
                break
        else:
            self.on_ground = False

        # Update the inventory and the crosshair and animate self
        self.animate(dt)

        # Update some position values
        self.coords = self.pos // BLOCK_SIZE
        self.chunk = self.coords // CHUNK_SIZE
        self.rect.topleft = self.pos - self.camera.pos

    def draw(self, screen: Surface, **kwargs) -> None:
        self.leg2.rect = self.leg2.image.get_rect(center=(self.rect.x+self.width/2, self.rect.y+72))
        screen.blit(self.leg2.image, self.leg2.rect.topleft)

        self.arm2.rect = self.arm2.image.get_rect(center=(self.rect.x+self.width/2, self.rect.y+35))
        screen.blit(self.arm2.image, self.arm2.rect.topleft)

        self.body.rect = self.body.image.get_rect(center=(self.rect.x+self.width/2, self.rect.y+51))
        screen.blit(self.body.image, self.body.rect.topleft)

        self.leg.rect = self.leg.image.get_rect(center=(self.rect.x+self.width/2, self.rect.y+72))
        screen.blit(self.leg.image, self.leg.rect.topleft)

        if self.inventory.holding:
            self.held_block = pygame.transform.rotate(pygame.transform.scale(BLOCK_TEXTURES[self.inventory.holding.name], inttup((BLOCK_SIZE * 0.34, BLOCK_SIZE * 0.34))), (self.arm.rot + (45 if abs(self.head.rot) > 90 else -45)) * 0.75)
            screen.blit(self.held_block, self.held_item_pos - VEC(self.held_block.get_size()) / 2 + VEC(12 if abs(self.head.rot) > 90 else -12, 0))

        self.arm.rect = self.arm.image.get_rect(center=(self.rect.x+self.width/2, self.rect.y+35))
        screen.blit(self.arm.image, self.arm.rect.topleft)

        self.head.rect = self.head.image.get_rect(center=(self.rect.x+self.width/2, self.rect.y+23))
        screen.blit(self.head.image, self.head.rect.topleft)

        self.leg.rect = self.leg.image.get_rect(center=(self.rect.x+self.width/2, self.rect.y+72))
        screen.blit(self.leg.image, self.leg.rect.topleft)

    def debug(self, screen: Surface, **kwargs) -> None:
        self.crosshair.debug(screen)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, width=1)
        # Draw the bottom bar (used to calculate if the player is on the ground)
        pygame.draw.rect(screen, (255, 0, 0), self.bottom_bar, width=2)
        for block in self.detecting_blocks: # Drawing the rects the player is calculating collision against
            pygame.draw.rect(screen, (255, 0, 0), block.rect, width=1)

    def animate(self, dt: float) -> None:
        """Calculate the rotation and facing of the player's body parts"""
        m_pos = VEC(pygame.mouse.get_pos())
        # Calculate head rotation based on the position of the player and the mouse
        self.head.rot = -VEC(self.head.rect.center).angle_to(m_pos-VEC(self.head.rect.center))-25

        if self.vel.x != 0:                              # If the player is moving in the horizontal direction
            self.leg.count += 12 * dt                   # A counter for the rotation of legs
            if abs(self.vel.x) > self.max_speed * 1.05:  # If the player is running at full speed
                self.leg.rot = cos(self.leg.count) * 40  # Rotate the legs out far (40)
            elif abs(self.vel.x) > self.max_speed * 0.5: # If the player is running at normal speed
                self.leg.rot = cos(self.leg.count) * 30  # Rotate the legs out normally (30)
            else:                                        # If the player is moving very slowly
                self.leg.rot = cos(self.leg.count) * 15  # Rotate the legs out a little bit (15)
            self.leg2.rot = -self.leg.rot                # Rotate the other leg in the opposite direction
            self.arm.rot = self.leg.rot * 0.8            # Rotate the arms slightly less than the legs
            self.arm2.rot = -self.arm.rot                # Rotate the other arm in the opposite direction
        else:
            self.leg.count = self.leg.rot = self.leg2.rot = self.arm.rot = self.arm2.rot = 0

        y_offset = player_arm_img.get_height() * cos(radians(self.arm.rot) * 0.65)
        x_offset = player_arm_img.get_height() * sin(radians(self.arm.rot) * 0.65)
        self.held_item_pos = VEC(self.body.rect.centerx, self.body.rect.top + 14) + VEC(x_offset + (24 if abs(self.head.rot) < 90 else -24), y_offset)

        rotate = pygame.transform.rotate
        if abs(self.head.rot) < 90: # If the player is facing right, flip the body and the head to the right
            self.head.image, self.body.image = rotate(player_head, self.head.rot), player_body
            self.arm.image, self.arm2.image = rotate(player_arm, self.arm.rot), rotate(player_arm, self.arm2.rot)
            self.leg.image, self.leg2.image = rotate(player_leg, self.leg.rot), rotate(player_leg, self.leg2.rot)
        else: # If the player is facing left, flip the body and the head to the left
            self.head.image, self.body.image = rotate(invert_player_head, self.head.rot-180), invert_player_body
            self.arm.image, self.arm2.image = rotate(invert_player_arm, self.arm.rot), rotate(invert_player_arm, self.arm2.rot)
            self.leg.image, self.leg2.image = rotate(invert_player_leg, self.leg.rot), rotate(invert_player_leg, self.leg2.rot)

    def move(self, blocks: dict[tuple[int, int], Block], dt: float) -> None:
        """Move the player and test for collision between it and the main dictionary of blocks"""
        # Number of steps to cut the movement into inside one frame to prevent tunnelling
        split = int(self.vel.length() * dt) + 1
        flag = False
        detecting_blocks = []

        for _ in range(split): # Split the movement
            # Only detect collision within a 3 by 4 area around the player
            for y in range(4):
                for x in range(3):
                    if (block_pos := (int(self.coords.x - 1 + x), int(self.coords.y - 1 + y))) in blocks: # If there exists a block at that position
                        # Get the block object in that position from the main blocks dictionary
                        block = blocks[block_pos]
                        if block.data["collision_box"] == "full": # If the block has a full collision box
                            # Here is some code for solving some rounding problems/bugs
                            # Bug description here vvv
                            # https://stackoverflow.com/questions/67419774/falling-left-and-right-inconsistencies-in-pygame-platformer
                            # DaNub is not going to attempt to explain why each "floor" and "ceil" are where they are so deal with it
                            if self.vel.y < 0:
                                colliding, detecting_blocks = block_collide(
                                    floor(self.pos.x), floor(self.pos.y + self.vel.y * dt / split),
                                    self.width, self.height,
                                    detecting_blocks, block)
                                if colliding:
                                    self.pos.y = floor(block.pos.y + BLOCK_SIZE)
                                    self.vel.y = 0
                                    flag = True
                            elif self.vel.y >= 0:
                                if self.vel.x <= 0:
                                    colliding, detecting_blocks = block_collide(
                                        floor(self.pos.x), ceil(self.pos.y + self.vel.y * dt / split),
                                        self.width, self.height,
                                        detecting_blocks, block)
                                    if colliding:
                                        self.pos.y = ceil(block.pos.y - self.height)
                                        self.vel.y = 0
                                        flag = True
                                elif self.vel.x > 0:
                                    colliding, detecting_blocks = block_collide(
                                        ceil(self.pos.x), ceil(self.pos.y + self.vel.y * dt / split),
                                        self.width, self.height,
                                        detecting_blocks, block)
                                    if colliding:
                                        self.pos.y = ceil(block.pos.y - self.height)
                                        self.vel.y = 0
                                        flag = True
            self.pos.y += self.vel.y * dt / split
            if flag: break

        # Same as the section of code above, but this section is also added to fix rounding issues
        flag = False
        for _ in range(split):
            for y in range(4):
                for x in range(3):
                    if (int(self.coords.x - 1 + x), int(self.coords.y - 1 + y)) in blocks:
                        block = blocks[(int(self.coords.x - 1 + x), int(self.coords.y - 1 + y))]
                        if block.data["collision_box"] == "full":
                            if self.vel.x < 0:
                                colliding, detecting_blocks = block_collide(
                                    floor(self.pos.x + self.vel.x * dt / split), floor(self.pos.y),
                                    self.width, self.height,
                                    detecting_blocks, block)
                                if colliding:
                                    self.pos.x = floor(block.pos.x + BLOCK_SIZE)
                                    self.vel.x = 0
                                    flag = True
                            elif self.vel.x >= 0:
                                colliding, detecting_blocks = block_collide(
                                    ceil(self.pos.x + self.vel.x * dt / split), ceil(self.pos.y),
                                    self.width, self.height,
                                    detecting_blocks, block)
                                if colliding:
                                    self.pos.x = ceil(block.pos.x - self.width)
                                    self.vel.x = 0
                                    flag = True
            self.pos.x += self.vel.x * dt / split
            if flag: break

        # Store the rects that are being tested for collision in self.detecting rects for debugging purposes
        self.detecting_blocks = detecting_blocks
        # Recalculating the position of the bottom bar
        self.bottom_bar.topleft = (self.rect.left + 1, self.rect.bottom)

    def break_block(self, chunks: dict, mpos: pygame.math.Vector2) -> None:
        """Break the block at the position of the mouse

        Args:
            chunks (dict): The main dictionary that contains the list of all chunks in the game
            mpos (Vector2): The position of the mouse
        """
        block_pos = inttup((self.pos + (mpos - self.rect.topleft)) // BLOCK_SIZE)
        neighbors = {
            "0 -1": inttup((block_pos[0], block_pos[1]-1)),
            "0 1": inttup((block_pos[0], block_pos[1]+1)),
            "-1 0": inttup((block_pos[0]-1, block_pos[1])),
            "1 0": inttup((block_pos[0]+1, block_pos[1]))
        }

        # If the block exists:
        if block_pos in Block.instances:
            if "unbreakable" in BLOCK_DATA[Block.instances[block_pos].name]: # And the block does not have the unbreakable tag:
                if BLOCK_DATA[Block.instances[block_pos].name]["unbreakable"]:
                    return
            # Remove it!
            remove_block(chunks, block_pos, Block.instances[block_pos].data, neighbors)

    # Please, dear god, never look at this function.
    # We tried it once and we are permanently blinded.
    # Save yourself :(
    def place_block(self, chunks: dict, mpos: Vector2) -> None:
        """Place a block at the position of the mouse

        Args:
            chunks (dict): The main dictionary that contains the list of all chunks in the game
            mpos (Vector2): The position of the mouse
        """
        if self.inventory.holding:
            # Get the coordinates and the neighbors of the block the crosshair is hovering over
            block_pos = inttup((self.pos + (mpos - self.rect.topleft)) // BLOCK_SIZE)
            if block_pos[1] < MAX_Y: # If the block is above the max y (there is bedrock there but why not /shrug)
                neighbors = {
                    "0 -1": inttup((block_pos[0], block_pos[1] - 1)),
                    "0 1": inttup((block_pos[0], block_pos[1] + 1)),
                    "-1 0": inttup((block_pos[0] - 1, block_pos[1])),
                    "1 0": inttup((block_pos[0] + 1, block_pos[1]))
                }
                # If a block has a counterpart (i.e. tall grass)
                if "counterparts" in BLOCK_DATA[self.inventory.holding.name]:
                    counterparts = BLOCK_DATA[self.inventory.holding.name]["counterparts"]
                    for counterpart in counterparts:
                        # Get the position of where counterpart would be and ITS neighbors
                        c_pos = VEC(block_pos)+VEC(inttup(counterpart.split(" ")))
                        c_neighbors = {
                            "0 -1": inttup((c_pos.x, c_pos.y - 1)),
                            "0 1": inttup((c_pos.x, c_pos.y + 1)),
                            "-1 0": inttup((c_pos.x - 1, c_pos.y)),
                            "1 0": inttup((c_pos.x + 1, c_pos.y))
                        }
                        # If the counterpart cannot be placed, break the entire loop and don't even place the original block
                        if not is_placeable(self, c_pos, BLOCK_DATA[counterparts[counterpart]], c_neighbors, second_block_pos=block_pos):
                            break
                    else: # If the for loop executed successfully without "break", continue on with placing the block
                        # Some "sec_block_pos" weirdness << descriptive commenting /j
                        # Note: DaNub forgot how this works so deal with it
                        # Note: trevor CBA to figure out how it works so deal with it
                        for counterpart in counterparts:
                            if not is_placeable(self, block_pos, BLOCK_DATA[self.inventory.holding.name], neighbors, second_block_pos=c_pos):
                                break
                        else:
                            set_block(chunks, block_pos, self.inventory.holding.name, neighbors)
                            for counterpart in counterparts:
                                # Get the position of where counterpart would be and ITS neighbors
                                c_pos = VEC(block_pos) + VEC(inttup(counterpart.split(" ")))
                                c_neighbors = {
                                    "0 -1": inttup((c_pos.x, c_pos.y - 1)),
                                    "0 1": inttup((c_pos.x, c_pos.y + 1)),
                                    "-1 0": inttup((c_pos.x - 1, c_pos.y)),
                                    "1 0": inttup((c_pos.x + 1, c_pos.y))
                                }
                                set_block(chunks, VEC(block_pos)+VEC(inttup(counterpart.split(" "))), counterparts[counterpart], c_neighbors)
                else:
                    # If the block does not have counterparts, place it if it can be placed
                    if is_placeable(self, block_pos, BLOCK_DATA[self.inventory.holding.name], neighbors):
                        set_block(chunks, block_pos, self.inventory.holding.name, neighbors)

    def pick_block(self) -> None:
        """Pick the block at the mouse position, with all the functionality in 3D Minecraft."""

        if block := self.crosshair.block:
            if "unpickblockable" in BLOCK_DATA[block.name]: return
            old_slot = self.inventory.holding  # Saving the original hotbar item
            if block.name in [item.name for item in self.inventory.items.values()]: # Checking if the desired item is in the inventory
                # Finding the inventory position of the desired item
                inventory_pos = [pos for pos, item in self.inventory.items.items() if item.name == block.name][0]
                if self.inventory.hotbar.selected in self.inventory.hotbar.items:
                    self.inventory.set_slot((self.inventory.hotbar.selected, 0), block.name) # Setting the hotbar slot to the desired item
                    self.inventory.set_slot(inventory_pos, old_slot.name)                    # Setting the original hotbar item to the old inventory position
                else:
                    self.inventory.set_slot((self.inventory.hotbar.selected, 0), block.name) # Setting the hotbar slot to the desired item
                    self.inventory.clear_slot(inventory_pos)                                 # Removing the item from the inventory position
            else:
                self.inventory.set_slot((self.inventory.hotbar.selected, 0), block.name) # Set the hotbar slot to the desired block
                if len(self.inventory.items) < self.inventory.max_items:                 # Add the old item to the inventory if there is enough space
                    self.inventory += old_slot.name

class Crosshair(Sprite):
    """The class responsible for the drawing and updating of the crosshair"""

    def __init__(self, master: Player, changeover: int, layer: LayersEnum = LayersEnum.CROSSHAIR) -> None:
        super().__init__(layer)
        self.master = master
        self.old_color = pygame.Color(0, 0, 0)
        self.new_color = pygame.Color(0, 0, 0)
        self.changeover = changeover # Changeover defines the speed that the colour changes from old to new
        self.mpos = VEC(pygame.mouse.get_pos())
        self.block_pos = inttup((self.master.pos + (self.mpos - self.master.rect.topleft)) // BLOCK_SIZE)
        self.block = None
        self.block_selection = self.BlockSelection(self, LayersEnum.BLOCK_SELECTION)
        self.grey = {*range(127 - 30, 127 + 30 + 1)} # A set that contains value from 97 to 157

    def update(self, dt: float, **kwargs) -> None:
        if self.new_color.r in self.grey and self.new_color.g in self.grey and self.new_color.b in self.grey:
            self.new_color = pygame.Color(255, 255, 255) # Checks if the colour is grey, and makes it white if it is

        self.new_color = pygame.Color(255, 255, 255) - self.new_color # Inverting the colour

        # Modified version of this SO answer, thank you!
        # https://stackoverflow.com/a/51979708/17303382
        self.old_color = [x + (((y - x) / self.changeover) * 100 * dt) for x, y in zip(self.old_color, self.new_color)]

        # Calculating the block beneath the mouse cursor
        self.mpos = VEC(pygame.mouse.get_pos())
        self.block_pos = inttup((self.master.pos + (self.mpos - self.master.rect.topleft)) // BLOCK_SIZE)
        if self.block_pos in Block.instances:
            self.block = Block.instances[inttup(self.block_pos)]
        else:
            self.block = None

    def draw(self, screen: pygame.Surface, **kwargs) -> None:
        if not constants.MANAGER.cinematic.value["CH"] or self.master.inventory.visible: return
        self.new_color = self.get_avg_color(screen) # I know this is cursed it's the easiest way ;-;

        # The 2 boxes that make up the crosshair
        pygame.draw.rect(screen, self.old_color, (self.mpos[0] - 2, self.mpos[1] - 16, 4, 32))
        pygame.draw.rect(screen, self.old_color, (self.mpos[0] - 16, self.mpos[1] - 2, 32, 4))

    def debug(self, screen: Surface, **kwargs) -> None:
        if not self.master.inventory.visible:
            if self.block:
                # Displays the name of the block below the mouse cursor next to the mouse
                screen.blit(text(self.block.name.replace('_', ' ').title(), color=(255, 255, 255)), (self.mpos[0] + 12, self.mpos[1] - 36))

    def get_avg_color(self, screen: Surface) -> pygame.Color:
        """Gets the average colour of the screen at the crosshair using the position of the mouse and the game screen.

        Returns:
            pygame.Color: The average colour at the position of the crosshair
        """

        try:
            surf = screen.subsurface((self.mpos[0] - 16, self.mpos[1] - 16, 32, 32))
            color = pygame.Color(pygame.transform.average_color(surf))
        except:
            try: # This try / except fixes a mouse OOB crash at game startup
                color = screen.get_at(inttup(self.mpos))
            except:
                color = pygame.Color(255, 255, 255)

        return color

    class BlockSelection(Sprite):
        def __init__(self, crosshair, layer: LayersEnum = LayersEnum.BLOCK_SELECTION):
            super().__init__(layer)
            self.crosshair = crosshair

        def draw(self, screen: Surface, **kwargs):
            # Drawing a selection box around the block beneath the mouse (but 2px larger than the block)
            if not constants.MANAGER.cinematic.value["CH"] or self.crosshair.master.inventory.visible: return
            if self.crosshair.block:
                pygame.draw.rect(screen, (0, 0, 0), Rect((self.crosshair.block.rect.left - 2, self.crosshair.block.rect.top - 2, BLOCK_SIZE + 4, BLOCK_SIZE + 4)), 2)