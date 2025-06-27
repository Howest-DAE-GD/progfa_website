"""
Created on 15/01/2025

 for globals
 over multiple python files

@author: Lennert
"""
from enum import Enum


# ERROR function printer
def print_error(error_type: str, prefix: str, suffix: str, error_cause: str = "unset error cause", continue_condition: bool = False):
    """
    prints an error
    basically useless

    :return: a false error code handy for when debugging
    """
    # color groups
    reset_color = "\033[0m" # resets ansi color to standard color
    main_error_color        = reset_color + "\033[30m" + "\033[101m"
    error_type_color        = reset_color + "\033[100m" + "\033[41m"
    sep_error_color         = reset_color + "\033[100m" + "\033[41m"
    error_description_color = reset_color + "\033[31m"
    error_cause_color       = reset_color + "\033[91m" + "\033[40m"
    error_continue          = reset_color + "\033[93m"

    print(f"{main_error_color}[ERROR]", end="") # [ERROR]
    print(f"{sep_error_color} × ", end="") #  ×
    if not error_type == "": print(f"{error_type_color}<{error_type}>", end="") # <error>
    else: print(f"{error_type_color}< ??? >", end="") # < ??? >
    print(f"{sep_error_color} ×", end="") # ×
    print(f"{error_description_color} {prefix}", end="") # prefix(
    print(f"{error_cause_color}{error_cause}", end="") # error_cause
    print(f"{error_description_color}{suffix}", end="") # )suffix

    if continue_condition:
        print(f"{error_continue} »»» {reset_color}", end="")
        print("× continue is not ready jet")

    print(reset_color)

def print_info(*args, sep = ' ', end = '', file = None):
    """
    exactly the same as print

    :param args: * -> is variable amount of elements needed for formated string with colors
    :param sep: separations
    :param end: end of scope
    :param file: print to a file.

    :return: -
    """
    if debugging :
        print(*args, sep, end)


# GLOBALS
process_intro_music = None
process_game_music  = None
debugging           = False