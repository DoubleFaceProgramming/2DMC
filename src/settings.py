from src.constants import CONF_DIR
from src.utils import pathof
import os
import json
from pathlib import Path

class Settings():
    def __init__(self) -> None:
        self.config = dict()
        self.reload()

    def reload(self):
            conf_files = list()
            conf_files_stems = list()
            for dirpath, _, files in os.walk(CONF_DIR):
                conf_files.extend([os.path.abspath(os.path.join(dirpath, file)) for file in files])
                conf_files_stems.extend([Path(file).stem for file in files])

            for index, file in enumerate(conf_files):
                self.config[conf_files_stems[index]] = json.loads(open(file, 'r').read())