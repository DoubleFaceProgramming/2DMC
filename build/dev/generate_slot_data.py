import pyperclip
import json
import re

# A horrifically messy script to generate identical grids of slot positions.

class IncorrectInputError(Exception): pass

def int_input(prompt: str) -> int:
    try:
        return int(input(prompt + ": "))
    except ValueError:
        raise IncorrectInputError("Please enter an integer.")

START_X = int_input("Enter the starting x pixel co-ordinate")
START_Y = int_input("Enter the starting y pixel co-ordinate")

SLOT_X = int_input("Enter the width of the slot")
SLOT_Y = int_input("Enter the height of the slot")

SLOT_BORDER_X = int_input("Enter the width of the border between slots")
SLOT_BORDER_Y = int_input("Enter the height of the border between slots")

ROWS = int_input("Enter the number of rows")
COLUMNS = int_input("Enter the number of columns")

slots = []

for i in range(ROWS):
    for j in range(COLUMNS):
        pos = (START_X + SLOT_X * j + SLOT_BORDER_X * j, START_Y + SLOT_Y * i + SLOT_BORDER_Y * i)
        slots.append({"pos": pos})

jsoned = json.dumps({"slots": slots}, indent=0)
jsoned = jsoned.replace("\n", " ")
jsoned = re.sub("^{ ", "{\n\t", jsoned)
jsoned = jsoned.replace("[ {", "[\n\t\t{")
jsoned = jsoned.replace("{ ", "{")
jsoned = jsoned.replace(" }", "}")
jsoned = jsoned.replace("[ ", "[")
jsoned = jsoned.replace(" ]", "]")
jsoned = jsoned.replace("}, ", "},\n\t\t")
jsoned = jsoned.replace("]}]}", "]}\n\t]\n}")

copy = True if input("Copy to clipboard? (y \\ n)\n") == "y" else False
if copy:
    pyperclip.copy(jsoned)
else:
    print(jsoned)