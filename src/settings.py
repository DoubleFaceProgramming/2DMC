from pygame.key import key_code
from src.utils import pathof
from pathlib import Path
import json
import os

class Settings():
    """Class that holds functions and dictionaries containing game settings / controls"""
    def __init__(self, confdir: str, confdirdefstem: str) -> None:
        self.confdir_def_stem = confdirdefstem # def -> default not definition
        self.confdir = pathof(confdir)
        self.confdir_def = os.path.join(self.confdir, self.confdir_def_stem)
        self.config = dict()
        self.init_config()

    def load(self) -> None:
        """Loading / reloading the configs from the .json files and parsing them"""

        # Getting all bottom level files and dirpath
        for dirpath, _, files in os.walk(self.confdir):
            if self.confdir_def_stem in dirpath:
                continue

            # Loops through all bottom level files, sets the key to the stem of the file (ex. keybinds not keybinds.json)
            # and the value to the parsed json content of the file
            # ex output. {'keybinds': {'jump': 'w', 'left': 'a', 'right': 'd' [...] }, 'scroll': {'reversed': False}}
            self.config.update({(filepath := Path(os.path.join(dirpath, file))).stem: json.loads(open(filepath, 'r').read()) for file in files})

    def init_config(self):
        """Creating default control settings"""

        for dirpath, _, files in os.walk(self.confdir_def):
            for file in files:
                # Making a path object for every new file and removing "default" from every path
                new_file = Path(os.path.join(dirpath, file).replace(self.confdir_def_stem, ''))
                if not new_file.exists():
                    # Creating the parent directories for the new file
                    if not (new_file_dirpath := new_file.parent).exists():
                        new_file_dirpath.mkdir()

                    # Writing the content of the default file into the new one
                    if not new_file.exists():
                        open(new_file, 'w').write(open(os.path.join(dirpath, file), 'r').read())

        # Generating the config attribute
        self.load()

    def get_pressed(self, action: str, keys: dict, mouse: dict) -> bool:
        """Gets whether the keybind associated with the action is being held down

        Args:
            action (str): The action to get the keybind from
            keys (dict): The dictionary returned from pygame.key.get_pressed()
            mouse (dict): The dictionary returned from pygame.mouse.get_pressed()

        Returns:
            bool: Whether the keybind associated with the action is currently being held down
        """

        # Mouse keybindings
        if self.config["keybinds"][action].startswith("mouse"):
            if (self.config["keybinds"][action] == "mouse_left"   and mouse[0]) or \
               (self.config["keybinds"][action] == "mouse_middle" and mouse[1]) or \
               (self.config["keybinds"][action] == "mouse_right"  and mouse[2]):
                return True
        # Keyboard keybindings
        else:
            return keys[key_code(self.config["keybinds"][action])]

    def get_pressed_short(self, action: str, eventkey: int) -> bool:
        """Returns whether the keybinding associated with the action was "tapped". Used in event loops

        Args:
            action (str): The action to get the keybind of
            eventkey (int): The event key or button to calculate the pressed state with: look at implementations

        Returns:
            bool: Whether the keybind was pressed or not
        """

        # Mouse keybindings
        if self.config["keybinds"][action].startswith("mouse"):
            if (self.config["keybinds"][action] == "mouse_left"   and eventkey == 1) or \
               (self.config["keybinds"][action] == "mouse_middle" and eventkey == 2) or \
               (self.config["keybinds"][action] == "mouse_right"  and eventkey == 3):
                return True
        # Keybord bindings
        elif eventkey == self.get_code(action):
            return True

    def get_code(self, action: str) -> int:
        """Gets the pygame keycode for the keybind for the given action

        Args:
            action (str): The action to get the keybind and keycode for

        Returns:
            int: The key code of the keybind of the action
        """

        return key_code(self.config["keybinds"][action])