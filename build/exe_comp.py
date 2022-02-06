from pathlib import Path
import sys
import os


BUNDLE_DIR = getattr(sys, '_MEIPASS', Path(os.path.abspath(os.path.dirname(__file__))).parent)

def pathof(file: str) -> str:
    """Gets the path to the given file that will work with exes.

    Args:
        file (str): The original path to go to

    Returns:
        str: The bundled - exe compatible file path
    """

    abspath = os.path.abspath(os.path.join(BUNDLE_DIR, file))
    if not os.path.exists(abspath):
        abspath = file
    return abspath
