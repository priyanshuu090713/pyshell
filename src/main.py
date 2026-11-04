import sys
import runpy
import pathlib as path
from termcolor import colored

while True :
    try :
        global i
        i = str(input(f"{path.Path.cwd()} {colored('>>>','red')}:\t"))
        runpy.run_path(f"func/{i}.py")
    except FileNotFoundError :
        print(f"Command {i} does not exist . retry", file=sys.stderr)
        continue
