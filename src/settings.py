from src.constants import CONF_DIR
from src.utils import pathof
import os
import json

class Settings():
    def __init__(self) -> None:
        #self.settings = dict()
        self.reload()

    def reload(self):
            conf_files = list()
            conf_files_raw = list()
            for dirpath, _, files in os.walk(CONF_DIR):
                conf_files.extend([os.path.abspath(os.path.join(dirpath, file)) for file in files])
                conf_files_raw.extend(files)

            for index, file in enumerate(conf_files):
                print(conf_files_raw[index] + str(json.loads(open(file, 'r').read())))

# settings.settings[peripherals][mouse][click][left]