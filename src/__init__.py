import build.exe_comp as exe_comp
import sys, os, pathlib
import src.utils.hooks

if not pathlib.Path(exe_comp.pathof(os.path.join("assets", "misc", "coconut.jpg"))).exists():
    sys.exit("Program received signal SIGSEGV, Segmentation fault. Error code: 0x1c0005c2")