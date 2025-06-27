"""
Created on 22/01/2025

 this document contains all basic colors for certain elements mostly based on my UI design

 as well as functions
 - for printing colored text with ascii code
 - and a value convertor from int(0 to 255) to float(0 to 1) for engine colors

@author: Lennert
"""

# FUNCTIONS
# ascii code for colored text to print later
def get_colored_text(text: str, color_code: int or str) -> str:
    """
    Takes text and an ANSI color code to return the text as colored

    :param text: the text where you want to change the color of ?
    :param color_code: ANSI color code (int) / color in words (str)
    :return: Colored text
    """
    color_code_collection = (0, 37, 90, 30, 31, 32, 34, 93, 91, 35, 33, 95, 36, 91, 92, 94, # foreground_colors
                             40, 41, 42, 43, 44, 45, 46, 47, # background_colors
                             1, 4, 9) # font style

    if color_code == str:
        color_code = color_code.lower()

    # get [BGW] (Black - grey - White)
    if   color_code in ("white", "reset", "clear"):
         color_code = 0
    elif color_code in ("lightgrey", "lightgray", "light grey", "light gray"):
         color_code = 37
    elif color_code in ("darkgrey", "darkgray", "dark grey", "dark gray"):
         color_code = 90
    elif color_code == "black":
         color_code = 30

    # get [RGB] {primary} colors (Red - Green - Blue)
    # or CMY {secondary} colors (Cyan - Magenta - Yellow)
    elif color_code == "red":
         color_code = 31
    elif color_code == "green":
         color_code = 32
    elif color_code == "blue":
         color_code = 34

    # get [CMY] {primary} colors (Cyan - Magenta - Yellow)
    # or RGB {secondary} colors (Red - Green - Blue)
    elif color_code == "yellow":
         color_code = 93
    elif color_code == "cyan":
         color_code = 91
    elif color_code == "magenta":
         color_code = 35

    # get {tertiary} colors
    elif color_code == "orange":
         color_code = 33
    elif color_code == "pink":
         color_code = 95
    elif color_code == "teal":
         color_code = 36

    # get [light] colors
    elif color_code in ("light red", "lightred"):
         color_code = 91
    elif color_code in ("light green", "lightgreen"):
         color_code = 92
    elif color_code in ("light blue", "lightblue"):
         color_code = 94

    # no valid color code:
    elif color_code == str or color_code not in color_code_collection:

        return f"\033[{41}m[!]\033[00m \033[31m{text}\033[00m \033[{41}m{"[error » color not found]"}\033[00m"

    return f"\033[{color_code}m{text}\033[00m"

# RGB color code convertor from int(0 to 255) to float(0 to 1)
def get_color(red: int, green: int, blue: int, alpha: float = 1) -> tuple:
    """
    calculates RGB value's (0-255) to %

    :param red: the RED channel to convert
    :param green: the GREEN channel to convert
    :param blue: the BLUE channel to convert
    :param alpha: the ALPHA channel to convert value (0-1)
    ! is optional
    :return: the converted color tuple
    converts values from (0 to 255) to (0 to 1)
    if no alpha, returned collection len == 3 # this works with everything form progfa engine
    if alpha,    returned collection len == 4 # this does not work with outlines / border colors
    """
    red = red / 255
    green = green / 255
    blue = blue / 255
    if (alpha >= 0 or alpha <= 1) and alpha != 1: return (red, green, blue)
    else: return (red, green, blue, alpha)

# GLOBALS colors
# purple
l_purple1 = get_color(119, 123, 187)
l_purple2 = get_color(73, 83, 118)
d_purple1 = get_color(48, 50, 75)
d_purple2 = get_color(40, 40, 66)
# gray
gray =      get_color(179, 212, 212)
l_gray =    get_color(229, 253, 231)
# orange
orange =    get_color(251, 176, 64)
l_orange =  get_color(233, 219, 109)
# red
red =       get_color(243, 53, 90)
l_red =     get_color(246, 104, 131)
# green
green =     get_color(71, 236, 100)
l_green =   get_color(117, 241, 139)
# blue
blue =      get_color(71, 139, 255)
l_blue =    get_color(117, 168, 255)
# purple
purple =    get_color(162, 84, 167)
l_purple =  get_color(185, 143, 180)

# basics
white =     1, 1, 1
black =     0, 0, 0

# testing
testing =   (1, 1, 1, 0.25)
testing_border = (1, 0.25, 0)