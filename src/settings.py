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
        self.init_config()

    def load(self):
        """Loading / reloading the configs from the .json files and parsing them"""

        conf_files = list()
        conf_files_stems = list()
        # Getting all bottom level files and dirpath
        for dirpath, _, files in os.walk(self.confdir):
            # Making a list of all the absolute paths to these files
            conf_files.extend([os.path.abspath(os.path.join(dirpath, file)) for file in files])
            # Making a list of all the names of these files (ex. keybinds not keybinds.json or conf\peripherals\keybinds.json)
            conf_files_stems.extend([Path(file).stem for file in files])

        # Looping through these files and setting the corresponding entry in the class dictionary to the file's data
        for index, file in enumerate(conf_files):
            self.config[conf_files_stems[index]] = json.loads(open(file, 'r').read())

    def init_config(self):
        """Creating default control settings"""

        for dirpath, _, files in os.walk(os.path.join(self.confdir, "default")):
            for file in files:
                # Getting the parts of the file, ex. ['conf', 'default', 'peripherals', 'keybinds.json']
                parts = list(Path(os.path.join(dirpath, file)).parts)
                # Removing the default so that the final directory is, ex, conf/peripherals/keybinds.json
                # not conf/default/peripherals/keybinds.json
                parts.remove("default") # Putting this on one line throws an error fsr xD
                # Joining the file back into 1 filepath
                new_file = '/'.join(parts)

                # Creating the parent directories for the new file
                new_file_dirpath = Path(Path(new_file).parent)
                if not new_file_dirpath.exists():
                    new_file_dirpath.mkdir()

                # Writing the content of the default file into the new one
                if not Path(new_file).exists():
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