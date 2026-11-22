
import ast
import math
import cmath
import numpy as np
import sys
import os

# ==========================================
# CALC.PY - Scientific & Complex Calculator
# ==========================================

VERSION = "1.0"

# ------------------------------------------
# Mathematical function dispatch
# ------------------------------------------

def universal(real_func, complex_func=None):
    """Choose math or cmath depending on the input."""
    def wrapper(x, *args):
        if isinstance(x, complex):
            if complex_func is None:
                raise ValueError("Function does not support complex input")
            return complex_func(x, *args)
        try:
            return real_func(x, *args)
        except ValueError:
            if complex_func is not None:
                return complex_func(x, *args)
            raise
    return wrapper


def complex_conjugate(x):
    return complex(x).conjugate()


def factorial(x):
    if isinstance(x, complex) or int(x) != x:
        raise ValueError("Factorial requires an integer")
    return math.factorial(int(x))


def gcd(*values):
    result = 0
    for value in values:
        result = math.gcd(result, int(value))
    return result


def lcm(*values):
    return math.lcm(*(int(x) for x in values))


def atan2(y, x):
    if isinstance(x, complex) or isinstance(y, complex):
        raise ValueError("atan2 requires real arguments")
    return math.atan2(y, x)


def statistics(func):
    def wrapper(values):
        return func(np.asarray(values))
    return wrapper


FUNCTIONS = {
    # Trigonometry
    "sin": universal(math.sin, cmath.sin),
    "cos": universal(math.cos, cmath.cos),
    "tan": universal(math.tan, cmath.tan),
    "asin": universal(math.asin, cmath.asin),
    "acos": universal(math.acos, cmath.acos),
    "atan": universal(math.atan, cmath.atan),
    "atan2": atan2,

    # Hyperbolic functions
    "sinh": universal(math.sinh, cmath.sinh),
    "cosh": universal(math.cosh, cmath.cosh),
    "tanh": universal(math.tanh, cmath.tanh),
    "asinh": universal(math.asinh, cmath.asinh),
    "acosh": universal(math.acosh, cmath.acosh),
    "atanh": universal(math.atanh, cmath.atanh),

    # Exponential and logarithmic
    "exp": universal(math.exp, cmath.exp),
    "log": universal(math.log, cmath.log),
    "log10": universal(math.log10, lambda x: cmath.log10(x)),
    "log2": universal(math.log2, lambda x: cmath.log(x, 2)),
    "log1p": math.log1p,
    "expm1": math.expm1,

    # Roots and powers
    "sqrt": universal(math.sqrt, cmath.sqrt),
    "cbrt": np.cbrt,

    # Rounding and numerical functions
    "ceil": math.ceil,
    "floor": math.floor,
    "trunc": math.trunc,
    "round": round,
    "abs": abs,
    "sign": np.sign,
    "hypot": math.hypot,
    "factorial": factorial,

    # Complex functions
    "phase": cmath.phase,
    "conj": complex_conjugate,
    "real": lambda x: complex(x).real,
    "imag": lambda x: complex(x).imag,
    "polar": cmath.polar,
    "rect": complex,

    # Number theory
    "gcd": gcd,
    "lcm": lcm,

    # Angle conversion
    "degrees": math.degrees,
    "radians": math.radians,

    # NumPy numerical functions
    "sinc": np.sinc,
    "mean": statistics(np.mean),
    "median": statistics(np.median),
    "std": statistics(np.std),
    "var": statistics(np.var),
    "sum": statistics(np.sum),
    "prod": statistics(np.prod),
    "min": np.min,
    "max": np.max,
}

# ------------------------------------------
# Constants and variable storage
# ------------------------------------------

CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "inf": math.inf,
    "nan": math.nan,
    "i": 1j,
    "j": 1j,
}

variables = {
    **CONSTANTS,
    "ans": 0
}

RESERVED = set(FUNCTIONS) | set(CONSTANTS) | {"ans"}

# ------------------------------------------
# Safe mathematical expression evaluator
# ------------------------------------------

BINARY_OPERATORS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.FloorDiv: lambda a, b: a // b,
    ast.Mod: lambda a, b: a % b,
    ast.Pow: lambda a, b: a ** b,
}

UNARY_OPERATORS = {
    ast.UAdd: lambda a: +a,
    ast.USub: lambda a: -a,
}


def evaluate(node):

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float, complex)):
            return node.value
        raise ValueError("Unsupported constant")

    if isinstance(node, ast.Name):
        if node.id in variables:
            return variables[node.id]
        raise NameError(f"Unknown variable: {node.id}")

    if isinstance(node, ast.BinOp):
        operator = BINARY_OPERATORS.get(type(node.op))
        if operator is None:
            raise ValueError("Unsupported operator")

        left = evaluate(node.left)
        right = evaluate(node.right)
        return operator(left, right)

    if isinstance(node, ast.UnaryOp):
        operator = UNARY_OPERATORS.get(type(node.op))
        if operator is None:
            raise ValueError("Unsupported unary operator")
        return operator(evaluate(node.operand))

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Invalid function call")

        name = node.func.id

        if name not in FUNCTIONS:
            raise NameError(f"Unknown function: {name}")

        if node.keywords:
            raise ValueError("Keyword arguments are not supported")

        arguments = [evaluate(arg) for arg in node.args]
        return FUNCTIONS[name](*arguments)

    if isinstance(node, (ast.List, ast.Tuple)):
        return [evaluate(element) for element in node.elts]

    raise ValueError(f"Unsupported expression: {type(node).__name__}")


def process(expression):

    expression = expression.strip()

    if not expression:
        return None

    try:
        tree = ast.parse(expression, mode="exec")

        if len(tree.body) != 1:
            raise ValueError("Enter one expression at a time")

        statement = tree.body[0]

        # Variable assignment
        if isinstance(statement, ast.Assign):

            if len(statement.targets) != 1:
                raise ValueError("Only single variable assignment is allowed")

            target = statement.targets[0]

            if not isinstance(target, ast.Name):
                raise ValueError("Invalid assignment target")

            name = target.id

            if name in RESERVED:
                raise ValueError(f"Cannot overwrite reserved name: {name}")

            value = evaluate(statement.value)
            variables[name] = value
            variables["ans"] = value

            return f"{name} = {value}"

        # Normal expression
        elif isinstance(statement, ast.Expr):
            result = evaluate(statement.value)
            variables["ans"] = result
            return result

        raise ValueError("Invalid statement")

    except SyntaxError:
        raise ValueError("Invalid mathematical expression")


# ------------------------------------------
# Terminal input - Ctrl+X support
# ------------------------------------------

def terminal_input():

    print("calc > ", end="", flush=True)

    if os.name == "nt":
        import msvcrt

        characters = []

        while True:
            char = msvcrt.getwch()

            if char == "\x18":
                return None

            if char in ("\r", "\n"):
                print()
                return "".join(characters)

            if char == "\x03":
                raise KeyboardInterrupt

            if char in ("\b", "\x7f"):
                if characters:
                    characters.pop()
                    print("\b \b", end="", flush=True)
                continue

            if char in ("\x00", "\xe0"):
                msvcrt.getwch()
                continue

            characters.append(char)
            print(char, end="", flush=True)

    else:
        import tty
        import termios

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        characters = []

        try:
            tty.setraw(fd)

            while True:
                char = sys.stdin.read(1)

                if char == "\x18":
                    return None

                if char in ("\r", "\n"):
                    print()
                    return "".join(characters)

                if char in ("\x03",):
                    raise KeyboardInterrupt

                if char in ("\x7f", "\x08"):
                    if characters:
                        characters.pop()
                        print("\b \b", end="", flush=True)
                    continue

                if char == "\x1b":
                    # Ignore terminal escape sequences
                    continue

                characters.append(char)
                print(char, end="", flush=True)

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


# ------------------------------------------
# Help
# ------------------------------------------

def show_help():

    print("""
    CALC.PY - Scientific & Complex Calculator
    -----------------------------------------

    OPERATORS:
        +   Addition
        -   Subtraction
        *   Multiplication
        /   Division
        //  Floor division
        %   Modulo
        **  Exponentiation

    TRIGONOMETRY:
        sin(x)   cos(x)   tan(x)
        asin(x)  acos(x)  atan(x)
        atan2(y, x)

    HYPERBOLIC:
        sinh(x)  cosh(x)  tanh(x)
        asinh(x) acosh(x) atanh(x)

    COMPLEX:
        i, j       Imaginary unit
        phase(x)   Complex argument
        conj(x)    Conjugate
        real(x)    Real component
        imag(x)    Imaginary component
        polar(x)   Polar representation
        rect(r, p) Polar to rectangular

    LOGARITHMS:
        log(x)     Natural logarithm
        log10(x)   Base 10
        log2(x)    Base 2
        log1p(x)   log(1+x)
        exp(x)     Exponential

    ROOTS:
        sqrt(x)    Square root
        cbrt(x)    Cube root

    OTHER:
        abs(x)     Absolute value / magnitude
        factorial(x)
        gcd(a, b)
        lcm(a, b)
        ceil(x)    floor(x)    trunc(x)
        degrees(x) radians(x)
        hypot(x, y)
        sinc(x)

    STATISTICS:
        mean([1, 2, 3])
        median([1, 2, 3])
        std([1, 2, 3])
        var([1, 2, 3])
        sum([1, 2, 3])
        prod([1, 2, 3])
        min([1, 2, 3])
        max([1, 2, 3])

    CONSTANTS:
        pi, e, tau, inf, nan, i, j

    VARIABLES:
        x = 10
        y = sin(x)
        ans

    ANGLES:
        Radians by default.
        Use radians() and degrees() for conversion.

    EXIT:
        Ctrl + X

    """)


# ------------------------------------------
# Main application
# ------------------------------------------

def main():

    os.system("cls" if os.name == "nt" else "clear")

    print("=" * 48)
    print("       CALC.PY | SCIENTIFIC CALCULATOR")
    print(f"                 Version {VERSION}")
    print("=" * 48)
    print("Standard + Complex + Trigonometric")
    print("Type help for functions and syntax.")
    print("Press Ctrl+X to exit.")
    print("-" * 48)

    while True:

        try:
            expression = terminal_input()

            if expression is None:
                break

            if expression.strip().lower() == "help":
                show_help()
                continue

            result = process(expression)

            if result is not None:
                print(f"  = {result}")

        except KeyboardInterrupt:
            print("\nUse Ctrl+X to exit.")

        except EOFError:
            break

        except Exception as error:
            print(f"  Error: {error}")

    print("\nCalculator terminated.")


if __name__ == "__main__":
    main()
