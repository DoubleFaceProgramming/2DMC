import pygame
from pygame.constants import K_a, K_d, K_w
from math import ceil, cos, floor

from src.constants import *
from src.utils import *
from src.images import *
from src.inventory import Inventory, Item
from src.block import *

class Camera(pygame.sprite.Sprite):
    def __init__(self, player):
        self.player = player
        self.pos = self.player.size / 2
        self.pos = self.player.pos - self.pos - VEC(SCR_DIM) / 2 + self.player.size / 2

    def update(self, dt):
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
        dist_squared = VEC(x_dist**2 if x_dist > 0 else -x_dist**2, y_dist**2*2.5 if y_dist > 0 else -y_dist**2*2.5)
        
        self.pos += (tick_offset / 10 + VEC(dist_squared) / 18000) * dt

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = VEC(0.225*BLOCK_SIZE, 1.8*BLOCK_SIZE)
        self.width, self.height = self.size.x, self.size.y
        self.start_pos = VEC(0, 3) * BLOCK_SIZE # Far lands: 9007199254740993 (aka 2^53)
        self.pos = VEC(self.start_pos)
        self.coords = self.pos // BLOCK_SIZE
        self.acc = VEC(0, 0)
        self.vel = VEC(0, 0)
        # Walking speed: 4.317 bps
        # Sprinting speed: 5.612 bps
        # Sprint-jumping speed: 7.127 bps
        self.max_speed = 5.153
        self.jumping_max_speed = 6.7
        self.rect = pygame.Rect((0, 0, 0.225*BLOCK_SIZE, 1.8*BLOCK_SIZE))
        self.bottom_bar = pygame.Rect((self.rect.x+1, self.rect.bottom), (self.width-2, 1))
        self.on_ground = False
        self.holding = "grass_block"
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
        
        self.inventory.add_item("grass_block")
        self.inventory.add_item("dirt")
        self.inventory.add_item("stone")
        self.inventory.add_item("grass")
        self.inventory.add_item("oak_log")
        self.inventory.add_item("oak_leaves")
        self.inventory.add_item("oak_planks")
        self.inventory.add_item("cobblestone")
        self.inventory.add_item("glass")
        self.inventory.add_item("poppy")
        self.inventory.add_item("dandelion")
        self.inventory.add_item("tall_grass")

    def update(self, blocks, m_state, dt):
        self.camera.update(dt)
        
        keys = pygame.key.get_pressed()
        if keys[K_a] and not self.inventory.visible:
            if self.vel.x > -self.max_speed:
                self.vel.x -= SLIDE * dt
        elif self.vel.x < 0:
            self.vel.x += SLIDE * dt
        if keys[K_d] and not self.inventory.visible:
            if self.vel.x < self.max_speed:
                self.vel.x += SLIDE * dt
        elif self.vel.x > 0:
            self.vel.x -= SLIDE * dt
        if keys[K_w] and self.on_ground and not self.inventory.visible:
            self.vel.y = -9.2
            self.vel.x *= 1.133
            if self.vel.x > self.jumping_max_speed:
                self.vel.x = self.jumping_max_speed
            elif self.vel.x < -self.jumping_max_speed:
                self.vel.x = -self.jumping_max_speed
        if -SLIDE * dt < self.vel.x < SLIDE * dt:
            self.vel.x = 0
        if self.vel.x > 0:
            self.direction = "right"
        elif self.vel.x < 0:
            self.direction = "left"

        self.acc.y = GRAVITY
        self.vel += self.acc * dt
        if self.vel.y > TERMINAL_VEL:
            self.vel.y = TERMINAL_VEL
        if self.on_ground:
            if self.vel.x < 0:
                self.vel.x += 0.03 * dt
            elif self.vel.x > 0:
                self.vel.x -= 0.03 * dt
                
        self.move(blocks, dt)
        self.bottom_bar = pygame.Rect((self.rect.left+1, self.rect.bottom), (self.width-2, 1))
                
        for block_rect in self.detecting_rects:
            if self.bottom_bar.colliderect(block_rect):
                self.on_ground = True
                break
            else: 
                self.on_ground = False

        self.coords = self.pos // BLOCK_SIZE
        self.chunk = self.coords // CHUNK_SIZE
        self.rect.topleft = self.pos - self.camera.pos
        self.animate(dt)
        
        self.inventory.update(m_state)
        self.crosshair.update(dt)

    def draw(self, screen, mpos):
        self.leg2.rect = self.leg2.image.get_rect(center=(self.rect.x+self.width/2, self.rect.y+72))
        screen.blit(self.leg2.image, self.leg2.rect.topleft)
        
        self.arm2.rect = self.arm2.image.get_rect(center=(self.rect.x+self.width/2, self.rect.y+35))
        screen.blit(self.arm2.image, self.arm2.rect.topleft)
        
        self.body.rect = self.body.image.get_rect(center=(self.rect.x+self.width/2, self.rect.y+51))
        screen.blit(self.body.image, self.body.rect.topleft)
        
        self.arm.rect = self.arm.image.get_rect(center=(self.rect.x+self.width/2, self.rect.y+35))
        screen.blit(self.arm.image, self.arm.rect.topleft)
        
        self.head.rect = self.head.image.get_rect(center=(self.rect.x+self.width/2, self.rect.y+23))
        screen.blit(self.head.image, self.head.rect.topleft)
        
        self.leg.rect = self.leg.image.get_rect(center=(self.rect.x+self.width/2, self.rect.y+72))
        screen.blit(self.leg.image, self.leg.rect.topleft)
        
        self.inventory.draw(screen)
        if not self.inventory.visible:
            self.crosshair.draw(screen, mpos)
        
    def debug(self, screen, mpos):
        self.crosshair.debug(screen, mpos)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, width=1)
        pygame.draw.rect(screen, (255, 0, 0), self.bottom_bar, width=2)
        for rect in self.detecting_rects:
            pygame.draw.rect(screen, (255, 0, 0), rect, width=1)

    def animate(self, dt):
        m_pos = VEC(pygame.mouse.get_pos())
        self.head.rot = -VEC(self.head.rect.center).angle_to(m_pos-VEC(self.head.rect.center))-25
        
        if self.vel.x != 0:
            self.leg.count += 0.2 * dt
            if abs(self.vel.x) > self.max_speed * 1.05:
                self.leg.rot = cos(self.leg.count) * 40
            elif abs(self.vel.x) > self.max_speed * 0.5:
                self.leg.rot = cos(self.leg.count) * 30
            else:
                self.leg.rot = cos(self.leg.count) * 15
            self.leg2.rot = -self.leg.rot
            self.arm.rot = self.leg.rot * 0.8
            self.arm2.rot = -self.arm.rot
        else:
            self.leg.count = self.leg.rot = self.leg2.rot = self.arm.rot = self.arm2.rot = 0
            
        if abs(self.head.rot) < 90:
            rotate = pygame.transform.rotate
            self.head.image, self.body.image = rotate(player_head, self.head.rot), player_body
            self.arm.image, self.arm2.image = rotate(player_arm, self.arm.rot), rotate(player_arm, self.arm2.rot)
            self.leg.image, self.leg2.image = rotate(player_leg, self.leg.rot), rotate(player_leg, self.leg2.rot)
        else:
            rotate = pygame.transform.rotate
            self.head.image, self.body.image = rotate(invert_player_head, self.head.rot-180), invert_player_body
            self.arm.image, self.arm2.image = rotate(invert_player_arm, self.arm.rot), rotate(invert_player_arm, self.arm2.rot)
            self.leg.image, self.leg2.image = rotate(invert_player_leg, self.leg.rot), rotate(invert_player_leg, self.leg2.rot)

    def move(self, blocks, dt):
        split = ceil(90 * dt / 62.5 * 1.5)
        flag = False
        detecting_rects = list()
        
        for _ in range(split):
            for y in range(4):
                for x in range(3):
                    if (int(self.coords.x-1+x), int(self.coords.y-1+y)) in blocks:
                        block = blocks[(int(self.coords.x-1+x), int(self.coords.y-1+y))]
                        if block.data["collision_box"] == "full":
                            if self.vel.y < 0:
                                colliding, detecting_rects = block_collide(
                                    floor(self.pos.x), floor(self.pos.y+self.vel.y/split), 
                                    self.width, self.height, 
                                    block, detecting_rects)
                                if colliding:
                                    self.pos.y = floor(block.pos.y + BLOCK_SIZE)
                                    self.vel.y = 0
                                    flag = True
                            elif self.vel.y >= 0:
                                if self.vel.x <= 0:
                                    colliding, detecting_rects = block_collide(
                                        floor(self.pos.x), ceil(self.pos.y+self.vel.y/split), 
                                        self.width, self.height, 
                                        block, detecting_rects)
                                    if colliding:
                                        self.pos.y = ceil(block.pos.y - self.height)
                                        self.vel.y = 0
                                        flag = True
                                elif self.vel.x > 0:
                                    colliding, detecting_rects = block_collide(
                                        ceil(self.pos.x), ceil(self.pos.y+self.vel.y/split), 
                                        self.width, self.height, 
                                        block, detecting_rects)
                                    if colliding:
                                        self.pos.y = ceil(block.pos.y - self.height)
                                        self.vel.y = 0
                                        flag = True
            self.pos.y += self.vel.y * dt / split
            if flag: break
            
        flag = False
        for _ in range(split):
            for y in range(4):
                for x in range(3):
                    if (int(self.coords.x-1+x), int(self.coords.y-1+y)) in blocks:
                        block = blocks[(int(self.coords.x-1+x), int(self.coords.y-1+y))]
                        if block.data["collision_box"] == "full":
                            if self.vel.x < 0:
                                colliding, detecting_rects = block_collide(
                                    floor(self.pos.x+self.vel.x/split), floor(self.pos.y), 
                                    self.width, self.height, 
                                    block, detecting_rects)
                                if colliding:
                                    self.pos.x = floor(block.pos.x + BLOCK_SIZE)
                                    self.vel.x = 0
                                    flag = True
                            elif self.vel.x >= 0:
                                colliding, detecting_rects = block_collide(
                                    ceil(self.pos.x+self.vel.x/split), ceil(self.pos.y), 
                                    self.width, self.height, 
                                    block, detecting_rects)
                                if colliding:
                                    self.pos.x = ceil(block.pos.x - self.width)
                                    self.vel.x = 0
                                    flag = True
            self.pos.x += self.vel.x * dt / split
            if flag: break
            
        self.detecting_rects = detecting_rects
        
    def break_block(self, chunks, mpos):
        block_pos = inttup((self.pos + (mpos - self.rect.topleft)) // BLOCK_SIZE)
        neighbors = {
            "0 -1": inttup((block_pos[0], block_pos[1]-1)),
            "0 1": inttup((block_pos[0], block_pos[1]+1)),
            "-1 0": inttup((block_pos[0]-1, block_pos[1])),
            "1 0": inttup((block_pos[0]+1, block_pos[1]))
        }
        if block_pos in Block.instances:
            remove_block(chunks, block_pos, Block.instances[block_pos].data, neighbors)
    
    def place_block(self, chunks, mpos):
        if self.holding:
            block_pos = inttup((self.pos + (mpos - self.rect.topleft)) // BLOCK_SIZE)
            neighbors = {
                "0 -1": inttup((block_pos[0], block_pos[1]-1)),
                "0 1": inttup((block_pos[0], block_pos[1]+1)),
                "-1 0": inttup((block_pos[0]-1, block_pos[1])),
                "1 0": inttup((block_pos[0]+1, block_pos[1]))
            }
            if "counterparts" in BLOCK_DATA[self.holding]:
                counterparts = BLOCK_DATA[self.holding]["counterparts"]
                for counterpart in counterparts:
                    c_pos = VEC(block_pos)+VEC(inttup(counterpart.split(" ")))
                    c_neighbors = {
                        "0 -1": inttup((c_pos.x, c_pos.y-1)),
                        "0 1": inttup((c_pos.x, c_pos.y+1)),
                        "-1 0": inttup((c_pos.x-1, c_pos.y)),
                        "1 0": inttup((c_pos.x+1, c_pos.y))
                    }
                    if not is_placeable(self, c_pos, BLOCK_DATA[counterparts[counterpart]], c_neighbors, c=block_pos):
                        break
                else:
                    for counterpart in counterparts:
                        if not is_placeable(self, block_pos, BLOCK_DATA[self.holding], neighbors, c=c_pos):
                            break
                    else:
                        set_block(chunks, block_pos, self.holding, neighbors)
                        for counterpart in counterparts:
                            c_pos = VEC(block_pos)+VEC(inttup(counterpart.split(" ")))
                            c_neighbors = {
                                "0 -1": inttup((c_pos.x, c_pos.y-1)),
                                "0 1": inttup((c_pos.x, c_pos.y+1)),
                                "-1 0": inttup((c_pos.x-1, c_pos.y)),
                                "1 0": inttup((c_pos.x+1, c_pos.y))
                            }
                            set_block(chunks, VEC(block_pos)+VEC(inttup(counterpart.split(" "))), counterparts[counterpart], c_neighbors)
            else:
                if is_placeable(self, block_pos, BLOCK_DATA[self.holding], neighbors):
                    set_block(chunks, block_pos, self.holding, neighbors)
                    
    def toggle_inventory(self):
        self.inventory.visible = not self.inventory.visible
        if self.inventory.visible:
            pygame.mouse.set_visible(True)
        else:
            pygame.mouse.set_visible(False)
            if self.inventory.selected:
                self.inventory.add_item(self.inventory.selected.name)
                self.inventory.selected = None
                
    def pick_block(self, mpos: pygame.math.Vector2) -> None:
        """Pick the block at the mouse position, with all the functionality in 3D Minecraft.

        Args:
            mpos (pygame.math.Vector2): The position of the mouse cursor, used to find the block the player is hovering over.
        """
        if block_name := self.crosshair.block_at_pos(mpos):
            # Saving the original hotbar item.
            old_slot = self.inventory.hotbar.items[self.inventory.hotbar.selected] 
            if block_name in [item.name for item in self.inventory.items.values()]:
                # Finding the inventory position of the desired item.                               
                inventory_pos = [pos for pos, item in self.inventory.items.items() if item.name == block_name][0] 
                if self.inventory.hotbar.selected in self.inventory.hotbar.items:  
                    # Setting the hotbar slot to the desired item.                               
                    self.inventory.set_slot((self.inventory.hotbar.selected, 0), block_name) 
                    # Setting the original hotbar item to the old inventory position.
                    self.inventory.set_slot(inventory_pos, old_slot.name) 
                else:   
                    # Setting the hotbar slot to the desired item.                                                                                          
                    self.inventory.set_slot((self.inventory.hotbar.selected, 0), block_name) 
                    # Removing the item from the inventory position
                    self.inventory.clear_slot(inventory_pos) 
            else: # If the item is not in the player's inventory:
                # Set the hotbar slot to the desired block.                                                                                                
                self.inventory.set_slot((self.inventory.hotbar.selected, 0), block_name)
                # Add the old item to the inventory if there is enough space.
                if len(self.inventory.items) < self.inventory.max_items:
                    self.inventory.add_item(old_slot.name)
        
class Crosshair():
    """The class responsible for the drawing and updating of the crosshair"""

    def __init__(self, master: Player, changeover: int) -> None:
        self.master = master
        self.old_color = pygame.Color(0, 0, 0)
        self.new_color = pygame.Color(0, 0, 0)
        self.changeover = changeover
        
    def update(self, dt: float) -> None:
        if 127-30 < self.new_color.r < 127+30 and 127-30 < self.new_color.g < 127+30 and 127-30 < self.new_color.b < 127+30:
            self.new_color = pygame.Color(255, 255, 255)
        self.new_color = pygame.Color(255, 255, 255) - self.new_color

        # Modified version of this SO answer, thank you!
        # https://stackoverflow.com/a/51979708/17303382
        self.old_color = [x + (((y - x) / self.changeover) * 100 * dt) for x, y in zip(self.old_color, self.new_color)]

    def draw(self, screen: pygame.Surface, mpos: pygame.math.Vector2) -> None:
        self.new_color = self.get_avg_color(screen, mpos) # I know this is cursed it's the easiest way ;-;
        pygame.draw.rect(screen, self.old_color, (mpos[0]-2, mpos[1]-16, 4, 32))
        pygame.draw.rect(screen, self.old_color, (mpos[0]-16, mpos[1]-2, 32, 4))
        
    def debug(self, screen: Surface, mpos):
        if not self.master.inventory.visible:
            if block := self.block_at_pos(mpos):
                screen.blit(text(block.replace('_', ' ').title(), color=(255, 255, 255)), (mpos[0]+12, mpos[1]-36))

    def get_avg_color(self, screen: pygame.Surface, mpos: pygame.math.Vector2) -> pygame.Color:
        """Gets the average colour of the screen at the crosshair using the position of the mouse and the game screen.

        Returns:
            pygame.Color: The average colour at the position of the crosshair
        """

        try:
            surf = screen.subsurface((mpos[0]-16, mpos[1]-16, 32, 32))
            color = pygame.Color(pygame.transform.average_color(surf))
        except:
            try:
                color = screen.get_at(inttup(mpos))
            except:
                color = pygame.Color(255, 255, 255)

        return color
    
    def block_at_pos(self, pos: Vector2) -> str or None:
        """Returns a string of the block at the position given

        Args:
            pos (Vector2): The position where the function should check. Should not be world space? Not sure xD
            player (Player): The player needed to find the onscreen position of the pos argument.

        Returns:
            str or None: Returns a string containing the name of the block at the position given,
                         or None if the block is not valid. ex. "grass_block"
        """
        block_pos = inttup((self.master.pos + (pos - self.master.rect.topleft)) // BLOCK_SIZE)
        if block_pos in Block.instances:
            return str(Block.instances[inttup(block_pos)].name)
        else: 
            return None