import sys
import runpy
import pathlib as path
import termcolor as t

while True :
    i = str(input(f"{t.colored(path.Path.cwd() , "grey") } {t.colored('>>>','red')}:\t")).lower()
    if i == "exit" or i == "kill" or i == "quit" or i == "q" :
        break
    try :
        runpy.run_path(f"func/{i}.py")
    except FileNotFoundError :
        try:
            print(exec(i))
        except NameError :
            print(f"attempted command {i} , does not exist in python commandline or in documented custom functions" , file=sys.stderr)
            continue
print(f"{t.colored("exiting")} : user requested exit")
