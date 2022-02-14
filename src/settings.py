from pygame.key import key_code
from src.utils import pathof
from pathlib import Path
from typing import Any
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

    def __getitem__(self, key: str) -> Any:
        return self.config[key]

    def get_conf_val(self, *keys, default: bool = False, return_dict: bool = False) -> Any:
        """Get the keybind of a config (needed so you can have nested dicts, like hotbar in keybinds.json)

        Args:
            keys (tuple of strings): A tuple of the path to the config , ex. ("scroll", "reversed") or
                            ("keybinds", "hotbar", "1")
            default (bool, optional): Get the default keybind. Defaults to False.
            return_dict (bool, optional): Return the dictionary, not its value. Used when changing the value.
                                          Defaults to False.

        Returns:
            Any: Returns the keybind (or dict) of the config
        """

        # The base level dict to initalise the variable
        sub_dict = (self.config if not default else self.config_def)[keys[0]]

        # Because we already have accessed keys[0] we can index from 1,
        # we index to -1 because thats the final value that we will change
        for key in keys[1:-1]:
            sub_dict = sub_dict[key] # Finding the bottom level dict
        # Returning the bind if not return_dict, else just returning the dictionary
        return sub_dict[keys[-1]] if not return_dict else sub_dict

    def load(self) -> None:
        """Loading / reloading the configs from the .json files and parsing them"""

        # Gets and loops through all bottom level files, and, if they are not in conf/default
        # sets the key to the stem of the file (ex. keybinds not keybinds.json)
        # and the value to the parsed json content of the file
        # ex output. {'keybinds': {'jump': 'w', 'left': 'a', 'right': 'd' [...] }, 'scroll': {'reversed': False}}
        self.config = {
            (Path(filepath := os.path.join(dirpath, file))).stem : json.loads(open(filepath, 'r').read())
            for dirpath, _, files in os.walk(self.confdir)
            for file in files
            if self.confdir_def_stem not in dirpath
        }

    def get_pressed(self, keys_pressed: dict, mouse_clicked: dict, *keys: tuple[str]) -> bool:
        """Gets whether the keybind associated with the setting is being held down

        Args:
            keys (dict): The dictionary returned from pygame.key.get_pressed()
            mouse (dict): The dictionary returned from pygame.mouse.get_pressed()
            keys (tuple of strings): A tuple of the path to the config , ex. ("scroll", "reversed") or
                                     ("keybinds", "hotbar", "1")

        Returns:
            bool: Whether the keybind associated with the setting is currently being held down
        """

        # Adding "keybinds" to the keys tuple so it is not necessary to pass it in
        if keys[0] != "keybinds":
            keys = ("keybinds", ) + keys

        # Handling unbound keybinds
        if not (keybind := str(self.get_conf_val(*keys))):
            return False
        # Mouse keybindings
        elif keybind.startswith("mouse"):
            if (keybind == "mouse_left"   and mouse_clicked[0]) or \
               (keybind == "mouse_middle" and mouse_clicked[1]) or \
               (keybind == "mouse_right"  and mouse_clicked[2]):
                return True
        # Keyboard keybindings
        else:
            return keys_pressed[key_code(keybind)]

    def get_pressed_short(self, eventkey: int, *keys: str) -> bool:
        """Returns whether the keybinding associated with the setting was "tapped". Used in event loops

        Args:
            eventkey (int): The event key or button to calculate the pressed state with: look at implementations
            keys (tuple of strings): A tuple of the path to the config , ex. ("scroll", "reversed") or
                                     ("keybinds", "hotbar", "1")

        Returns:
            bool: Whether the keybind was pressed or not
        """

        # Adding "keybinds" to the keys tuple so it is not necessary to pass it in
        if keys[0] != "keybinds":
            keys = ("keybinds", ) + keys

        # Handling unbound keybinds
        if not (keybind := str(self.get_conf_val(*keys))):
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

    def set_config(self, new: str, *keys: tuple[str]) -> None:
        """Change the desired keybind to the given new one

        Args:
            new (str): The key / mouse button to change it to, ex. 'y', "mouse_left"
            keys (tuple of strings): A tuple of the path to the config , ex. ("scroll", "reversed") or
                                     ("keybinds", "hotbar", "1")
        """

        # Changing the value, note the use of return dict so we actually change the dict instead of
        # creating a local variable, and keys[-1] to get the name of the config (ex. "jump")
        self.get_conf_val(*keys, return_dict=True)[keys[-1]] = new

        # Writing the updated config into its  respective file
        open(self.file_paths[keys[0]], 'w').write(json.dumps(self[keys[0]], indent = 4))

    # The following functions are not strictly necessary
    # but will provide a cleaner implentation in the future

    def is_default(self, *keys: tuple[str]) -> bool:
        """Checks if the given keybind is the default for that keybind

        Args:
            keys (tuple of strings): A tuple of the path to the config , ex. ("scroll", "reversed") or
                                     ("keybinds", "hotbar", "1")

        Returns:
            bool: Whether the given keybind is the default or not
        """

        # default=False not necessary but looks better imo :P
        return self.get_conf_val(*keys, default=False) == self.get_conf_val(*keys, default=True)

    def reset_config(self, *keys: tuple[str]) -> None:
        """Reset the given setting to its default

        Args:
            keys (tuple of strings): A tuple of the path to the config , ex. ("scroll", "reversed") or
                                     ("keybinds", "hotbar", "1")
        """

        # Setting the config to its default value
        self.set_config(self.get_conf_val(*keys, default=True), *keys)