DEBUG = 3
INFO = 2
NORMAL = 1
QUIET = 0

verbosity = QUIET


def debug(string):
    if verbosity >= DEBUG:
        print(f"[d] {string}")

def info(string):
    if verbosity  >= INFO:
        print(f"[i] {string}")

def echo(string):
    if verbosity >= NORMAL:
        print(f"[*] {string}")

def warn(string):
    if verbosity >= NORMAL:
        print(f"[!] {string}")

def error(string):
    if verbosity >= QUIET:
        print(f"[!] {string}")

def get(string):
    return input(f"[#] {string}")

def init(v_level):
    global verbosity

    verbosity = v_level
