from numpy import e, true_divide
import pygame
from pygame.mouse import get_pressed
from pygame.key import key_code
from src.utils import pathof
from pathlib import Path
import json
import os

class Settings():
    """Class that holds functions and dictionaries containing game settings / controls"""
    def __init__(self, confdir) -> None:
        self.confdir = pathof(confdir)
        self.config = dict()
        self.load()

    def load(self, default: bool = False):
        """Loading / reloading the configs from the .json files and parsing them"""

        conf_files = list()
        conf_files_stems = list()
        for dirpath, _, files in os.walk(self.confdir):
            conf_files.extend([os.path.abspath(os.path.join(dirpath, file)) for file in files])
            conf_files_stems.extend([Path(file).stem for file in files])

        for index, file in enumerate(conf_files):
            self.config[conf_files_stems[index]] = json.loads(open(file, 'r').read())
            if not default:
                del self.config[conf_files_stems[index]]["default"]

        if default:
            for category in self.config:
                self.config[category] = self.config[category]["default"]

    def get_pressed(self, action: str, keys: dict, mouse: dict) -> bool:
        if self.config["keybinds"][action].startswith("mouse"):
            if (self.config["keybinds"][action] == "mouse_left" and mouse[0]) or \
               (self.config["keybinds"][action] == "mouse_middle" and mouse[1]) or \
               (self.config["keybinds"][action] == "mouse_right" and mouse[2]):
                return True
        else:
            return keys[key_code(self.config["keybinds"][action])]

    def get_pressed_short(self, action, eventkey: int):
        if self.config["keybinds"][action].startswith("mouse"):
            if (self.config["keybinds"][action] == "mouse_left" and eventkey == 1) or \
               (self.config["keybinds"][action] == "mouse_middle" and eventkey == 2) or \
               (self.config["keybinds"][action] == "mouse_right" and eventkey == 3):
                return True
        elif eventkey == self.get_code(action):
            return True

    def get_code(self, action: str) -> int:
        return key_code(self.config["keybinds"][action])