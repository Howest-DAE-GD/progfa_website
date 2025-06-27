"""
Created on 22/01/2025

 this document contains all basic fonts
 - strong fonts for titles and mostly everything else
 - normal fonts for paragraphs and such basic text
 - mono   fonts for equal spacing between characters, handy for scores and cases where you want to align the text left precisely

 it also contains the basic font sizes
 - strong font size = the biggest font size
 - normal font size = a big font size, to read easy
 - mono   font size = a more normal font size that looks small because the others are so big

@author: Lennert
"""
# FUNCTIONS
def lowercase_variables(variable: str or tuple or list or set) -> str or tuple or list or set:
    """
    sets collections of strings to lowercase

    :param variable: the variable you want to make all content lowercase

    :return: new collection with lowercase content
    """
    # LOCALS
    collection = list()
    new_collection = list()

    input_type = -1
    # -1 == no value
    # 0  == string()
    # 1  == tuple()
    # 2  == list()
    # 3  == set()
    # to return the same type as the type of the inputed parameter

    # type CONTROL
    # » string
    if type(variable) == str:
        variable = variable.lower()
        input_type = 0 # type == string

    # » collections
    if type(variable) == tuple:
        collection = list(variable)
        input_type = 1 # type == tuple
    elif type(variable) == list:
        collection = list(variable)
        input_type = 2 # type == list
    elif type(variable) == set:
        collection = list(variable)
        input_type = 3 # type == set

    if input_type == -1:
        print("error, type is not valid, parameter value is not valid")

    if input_type in (1, 2, 3):
        for variable in collection:
            if not type(variable) == str: continue
            new_collection.append(variable.lower())
            print(new_collection)
        collection = new_collection

    if input_type == 0: return str(variable)
    if input_type == 1: return tuple(collection)
    if input_type == 2: return list(collection)
    if input_type == 3: return set(collection)

def clean_string(variable: str or tuple or list or set) -> str or tuple or list or set:
    pass

# GLOBALS
# fonts paths
normal_font =           "fonts/normal/normal.otf"          # not used
normal_bold_font =      "fonts/normal/normal_bold.otf"     # not used

mono_font =             "fonts/mono/mono.otf"
mono_bold_font =        "fonts/mono/mono_bold.otf"
mono_italic_font =      "fonts/mono/mono_italic.otf"
mono_bold_italic_font = "fonts/mono/mono_bold_italic.otf"

strong_font =           "fonts/strong/strong.otf"

# sizes
heading_text_size = 20
normal_text_size = 16
testing_text_size = 10