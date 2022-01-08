import pygame
from pygame.constants import K_0, K_1, K_9
import time

from src.constants import *
from src.utils import *
from src.images import *

class Item(object):
    def __init__(self, name):
        self.name = name
        self.count = 1
        self.nbt = {}

class Inventory(object):
    def __init__(self, player):
        self.player = player
        self.slot_start = VEC(400, 302)
        self.slot_size = (40, 40)
        self.items = {}
        self.hotbar = Hotbar(self)
        self.visible = False
        self.selected = None
        self.hovering = None
        self.max_items = 36
        self.transparent_background = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
        self.transparent_background.fill((0, 0, 0, 125))

    def update(self, m_state):
        if self.visible:
            mpos = VEC(pygame.mouse.get_pos())
            y_test = self.slot_start.y < mpos.y < self.slot_start.y+(self.slot_size[1]+5)*3
            x_test = self.slot_start.x < mpos.x < self.slot_start.x+(self.slot_size[0]+5)*9
            hotbar_y_test = 446 < mpos.y < 446+(self.slot_size[1]+5)
            
            if y_test:
                self.hovering = inttup(((mpos.x-self.slot_start.x)//(self.slot_size[0]+5), (mpos.y-self.slot_start.y)//(self.slot_size[1]+5)+1))
            elif hotbar_y_test:
                self.hovering = inttup(((mpos.x-400)//(self.slot_size[0]+5), 0))
            else:
                self.hovering = None
            if m_state == 1 and (y_test or hotbar_y_test) and x_test:
                if self.hovering in self.items:
                    if not self.selected:
                        self.selected = self.items[self.hovering]
                        self.clear_slot(self.hovering)
                    else:
                        tmp = self.selected
                        self.selected = self.items[self.hovering]
                        self.set_slot(self.hovering, tmp.name)
                else:
                    if self.selected:
                        self.set_slot(self.hovering, self.selected.name)
                        self.selected = None
                        
        if m_state == 4 or m_state == 5:
            self.hotbar.update(m_state)
        else:
            self.hotbar.update(0)

    def draw(self, screen):
        self.hotbar.draw(screen)
        if self.visible:
            screen.blit(self.transparent_background, (0, 0))
            screen.blit(inventory_img, (VEC(SCR_DIM)/2-VEC(inventory_img.get_width()/2, inventory_img.get_height()/2)))
            
            for slot in self.items:
                item_img = pygame.transform.scale(block_textures[self.items[slot].name], self.slot_size)
                if slot[1] != 0:
                    screen.blit(item_img, self.slot_start+VEC(slot[0]*(self.slot_size[0]+5), (slot[1]-1)*(self.slot_size[1]+5)))
                else:
                    screen.blit(item_img, self.slot_start+VEC(0, 190)+VEC(slot[0]*(self.slot_size[0]+5), (slot[1]-1)*(self.slot_size[1]+5)))
            if self.selected:
                screen.blit(pygame.transform.scale(block_textures[self.selected.name], inttup(VEC(self.slot_size)*0.9)), VEC(pygame.mouse.get_pos())-VEC(self.slot_size)*0.45)
            if self.hovering in self.items:
                name = self.items[self.hovering].name.replace("_", " ").capitalize()
                mpos = pygame.mouse.get_pos()
                if self.selected == None:
                    surf, pos = create_text_box(smol_text(name), (mpos[0]+12, mpos[1]-24), 255)
                    screen.blit(surf, pos)
                    
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

    def set_slot(self, slot, item):
        self.items[slot] = Item(item)

    def clear_slot(self, slot):
        del self.items[slot]

    def add_item(self, item):
        for y in range(4):
            for x in range(9):
                if not (x, y) in self.items:
                    self.items[(x, y)] = Item(item)
                    return True
        return False

class Hotbar(object):
    def __init__(self, inventory):
        self.slot_start = VEC(WIDTH/2-hotbar_img.get_width()/2, HEIGHT-hotbar_img.get_height())
        self.slot_size = (40, 40)
        self.inventory = inventory
        items = {}
        for slot in self.inventory.items:
            if slot[1] == 0:
                items[slot[0]] = self.inventory.items[slot]
        self.items = items
        self.selected = 0
        self.fade_timer = 0

    def update(self, scroll):
        hotbar_items = {}
        for slot in self.inventory.items:
            if slot[1] == 0:
                hotbar_items[slot[0]] = self.inventory.items[slot]

        self.items = hotbar_items
        if not self.inventory.visible:
            keys = pygame.key.get_pressed()
            for i in range(K_1, K_9+1):
                if keys[i]:
                    self.selected = i-K_0-1
                    self.fade_timer = time.time()
                    
            if scroll == 4:
                if self.selected == 0:
                    self.selected = 8
                else:
                    self.selected -= 1
            elif scroll == 5:
                if self.selected == 8:
                    self.selected = 0
                else:
                    self.selected += 1
                    
            if scroll:
                self.fade_timer = time.time()
                
        if self.selected in self.items:
            self.inventory.player.holding = self.items[self.selected].name
        else:
            self.inventory.player.holding = None

    def draw(self, screen):
        screen.blit(hotbar_img, self.slot_start)
        screen.blit(hotbar_selection_img, (self.slot_start-VEC(2, 2)+VEC(self.slot_size[0]+10, 0)*self.selected))
        for slot in self.items:
            item_img = pygame.transform.scale(block_textures[self.items[slot].name], self.slot_size)
            screen.blit(item_img, self.slot_start+VEC(8, 0)+VEC(slot*(self.slot_size[0]+10), 8))
            
        if (time_elapsed := time.time() - self.fade_timer) < 3:
            if self.selected in self.items:
                opacity = 255 * (3-time_elapsed) if time_elapsed > 2 else 255
                blitted_text = smol_text(self.items[self.selected].name.replace("_", " ").capitalize())
                surf, pos = create_text_box(blitted_text, (WIDTH/2-blitted_text.get_width()/2-8, HEIGHT-92), opacity)
                screen.blit(surf, pos)