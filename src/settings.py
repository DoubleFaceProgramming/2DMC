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
        self.file_paths = dict()
        self.config_def = dict()
        self.config = dict()

        # Getting bottom level files
        for dirpath, _, files in os.walk(self.confdir_def):
            for file in files:
                # Making a path object for every new file and removing "default" from every path
                new_file = Path((old_path := os.path.join(dirpath, file)).replace(self.confdir_def_stem, ''))

                # Content of the default file
                def_content = open(old_path, 'r').read()
                if not new_file.exists():
                    # Creating the parent directories for the new file
                    if not (new_file_dirpath := new_file.parent).exists():
                        new_file_dirpath.mkdir()

                    # Writing the content of the default file into the new one
                    open(new_file, 'w').write(def_content)

                # Writing the default file content into the default controls dictionary: see comprehension in
                # Settings.load() for details
                self.config_def.update({Path(old_path).stem : json.loads(def_content)})
                # Writing the file path for each "catergory" of setting
                # ex. {"keybinds": "conf\\peripherals\\keybinds.json", "scroll": "conf\\peripherals\\mouse\\scroll.json"}
                self.file_paths[Path(old_path).stem] = str(new_file)

        # Generating the config attribute
        self.load()

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

    def set_keybind(self, catergory: str, action: str, new: str) -> None:
        """Change the desired keybind to the given new one

        Args:
            catergory (str): The catergory of setting, ex. "keybinds", "scroll"
            action (str): The specific action to change, ex. "left", "reversed"
            new (str): The key / mouse button to change it to, ex. 'y', "mouse_left"
        """

        self.config[catergory][action] = new
        # Writing the updated configs into their respective files
        open(self.file_paths[catergory], 'w').write(json.dumps(self.config[catergory], indent = 4))

    def is_default(self, catergory: str, action: str) -> bool:
        """Checks if the given keybind is the default for that keybind

        Args:
            catergory (str): The catergory of the setting, ex. "keybinds", "scroll"
            action (str): The specific action to check, ex. "left", "reversed"

        Returns:
            bool: Whether the given keybind is the default or not
        """

        return self.config[catergory][action] == self.config_def["keybinds"][action]

    def get_pressed(self, action: str, keys: dict, mouse: dict) -> bool:
        """Gets whether the keybind associated with the action is being held down

        Args:
            action (str): The action to get the keybind from
            keys (dict): The dictionary returned from pygame.key.get_pressed()
            mouse (dict): The dictionary returned from pygame.mouse.get_pressed()

        Returns:
            bool: Whether the keybind associated with the action is currently being held down
        """

        # Handling unbound keybinds
        if not (keybind := self.config["keybinds"][action]):
            return False
        # Mouse keybindings
        elif keybind.startswith("mouse"):
            if (keybind == "mouse_left"   and mouse[0]) or \
               (keybind == "mouse_middle" and mouse[1]) or \
               (keybind == "mouse_right"  and mouse[2]):
                return True
        # Keyboard keybindings
        else:
            return keys[key_code(keybind)]

    def get_pressed_short(self, action: str, eventkey: int) -> bool:
        """Returns whether the keybinding associated with the action was "tapped". Used in event loops

        Args:
            action (str): The action to get the keybind of
            eventkey (int): The event key or button to calculate the pressed state with: look at implementations

        Returns:
            bool: Whether the keybind was pressed or not
        """

        # Handling unbound keybinds
        if not (keybind := self.config["keybinds"][action]):
            return False
        # Mouse keybindings
        elif keybind.startswith("mouse"):
            if (keybind == "mouse_left"   and eventkey == 1) or \
               (keybind == "mouse_middle" and eventkey == 2) or \
               (keybind == "mouse_right"  and eventkey == 3):
                return True
        # Keybord bindings
        elif eventkey == key_code(keybind):
            return True