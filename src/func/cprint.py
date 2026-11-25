from colorama import Fore, Style, init

init(autoreset=True)

colors = {
    "red": Fore.RED,
    "green": Fore.GREEN,
    "blue": Fore.BLUE,
    "yellow": Fore.YELLOW,
    "cyan": Fore.CYAN,
    "magenta": Fore.MAGENTA,
    "white": Fore.WHITE,
    "grey": Fore.LIGHTBLACK_EX
}

print(colors[input("enter text color").lower()] + input("enter colored string"))
