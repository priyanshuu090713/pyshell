import sys
import runpy
import pathlib as path
from colorama import Fore, Style, init

init(autoreset=True)

while True :
    i = str(input(f"{Fore.LIGHTBLACK_EX}{path.Path.cwd()} {Fore.RED}>>>:\t")).lower()
    if i == "exit" or i == "kill" or i == "quit" or i == "q" :
        break
    try :
        runpy.run_path(f"func/{i}.py")
    except FileNotFoundError :
        try:
            print(eval(i))
        except NameError :
            print(f"attempted command {i} , does not exist in python commandline or in documented custom functions" , file=sys.stderr)
            continue
print(f"{Fore.RED}exiting{Style.RESET_ALL} : user requested exit")
