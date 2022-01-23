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

                # Writing the default file content into the default controls dictionary: see comprehension in
                # Settings.load() for details
                self.config_def.update({Path(old_path).stem : json.loads((def_content := open(old_path, 'r').read()))})
                # Writing the file path for each "category" of setting
                # ex. {"keybinds": "conf\\peripherals\\keybinds.json", "scroll": "conf\\peripherals\\mouse\\scroll.json"}
                self.file_paths[Path(old_path).stem] = str(new_file)

                if not new_file.exists():
                    # Creating the parent directories for the new file
                    if not (new_file_dirpath := new_file.parent).exists():
                        new_file_dirpath.mkdir()

                    # Writing the content of the default file into the new one
                    open(new_file, 'w').write(def_content)

        # Generating the config attribute
        self.load()

    def load(self) -> None:
        """Loading / reloading the configs from the .json files and parsing them"""

        # Gets and loops through all bottom level files, and, if they are not in conf/default
        # sets the key to the stem of the file (ex. keybinds not keybinds.json)
        # and the value to the parsed json content of the file
        # ex output. {'keybinds': {'jump': 'w', 'left': 'a', 'right': 'd' [...] }, 'scroll': {'reversed': False}}
        self.config = {
            (Path(filepath := os.path.join(dirpath, file))).stem : json.loads(open(filepath, 'r').read())
            for dirpath, _, files in os.walk(self.confdir) for file in files if self.confdir_def_stem not in dirpath
        }

    def get_pressed(self, setting: str, keys: dict, mouse: dict) -> bool:
        """Gets whether the keybind associated with the setting is being held down

        Args:
            setting (str): The setting to get the keybind from
            keys (dict): The dictionary returned from pygame.key.get_pressed()
            mouse (dict): The dictionary returned from pygame.mouse.get_pressed()

        Returns:
            bool: Whether the keybind associated with the setting is currently being held down
        """

        # Handling unbound keybinds
        if not (keybind := self.config["keybinds"][setting]):
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

    def get_pressed_short(self, setting: str, eventkey: int) -> bool:
        """Returns whether the keybinding associated with the setting was "tapped". Used in event loops

        Args:
            setting (str): The setting to get the keybind of
            eventkey (int): The event key or button to calculate the pressed state with: look at implementations

        Returns:
            bool: Whether the keybind was pressed or not
        """

        # Handling unbound keybinds
        if not (keybind := self.config["keybinds"][setting]):
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

    # The following functions are not strictly necessary
    # but provide a cleaner implentation for the future

    def set_keybind(self, category: str, setting: str, new: str) -> None:
        """Change the desired keybind to the given new one

        Args:
            category (str): The category of setting, ex. "keybinds", "scroll"
            setting (str): The specific setting to change, ex. "left", "reversed"
            new (str): The key / mouse button to change it to, ex. 'y', "mouse_left"
        """

        self.config[category][setting] = new
        # Writing the updated configs into their respective files
        open(self.file_paths[category], 'w').write(json.dumps(self.config[category], indent = 4))

    def is_default(self, category: str, setting: str) -> bool:
        """Checks if the given keybind is the default for that keybind

        Args:
            category (str): The category of the setting, ex. "keybinds", "scroll"
            setting (str): The specific setting to check, ex. "left", "reversed"

        Returns:
            bool: Whether the given keybind is the default or not
        """

        return self.config[category][setting] == self.config_def["keybinds"][setting]

    def reset_config(self, category: str, setting: str) -> None:
        """Reset the given setting to its default

        Args:
            category (str): The category of the setting, ex. "keybinds", "scroll"
            setting (str): The specific setting to change, ex. "left", "reversed"
        """

        self.set_keybind(category, setting, self.config_def[category][setting])