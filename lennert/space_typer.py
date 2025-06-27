#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 29/11/2024

 main file, pygame engine

@author: Lennert
"""

# TODO:
#  ¬ flare's
#    - make it add_flare() # when losing a letter ONLY
#      (adds values to globals, in order for it to exist and able to be shown)
#    - fix the draw_flare() # draw's the flares
#    - make update_flare() # updates the position and velocity
#      (applying the velocity to the position, so it will move)
#    - make check_flare() # checks if flares are visible,
#      (deletes values to flare globals, to delete the flare)
#      (deleting is needed for memory space)

# IMPORTS
import progfa.progfa_engine as     pfe
from   progfa.progfa_engine import ShapeMode
from   progfa.progfa_engine import MouseButton

from   enum import Enum   # game states (state machine)

import pygame             # the base of the progfa library
# import pygame.mixer_music # music player

import math               # for 'advanced' math calculations
import random             # for annoying 8bit beep sounds

# individual files
import libraries.common    as common           # basic      globals
import libraries.calc      as calc             # 'advanced' calculations
import libraries.colors    as colors           # basic      colors
import libraries.fonts     as fonts            # basic      fonts
import libraries.sound     as sound            # basic      sounds and music
import storage.collections as word_collections # basic      word collections + add-ons

# GLOBALS

# Create an instance of ProgfaEngine and set window size (width, height):
viewport_scaler = 1      # (variable) change this value if you want to change the viewport size (make sure the radius of 4 by 3 isn't broken)
general_scale   = 300    # (constant) stay off
aspect_ratio    = (4, 3) # (constant) stay off
engine = pfe.ProgfaEngine(int(general_scale * aspect_ratio[0] * viewport_scaler), int(general_scale * aspect_ratio[1] * viewport_scaler))
common.print_info(f"\nviewport info: \n{colors.get_colored_text(f"{engine.width}", 'yellow')} : {colors.get_colored_text(f"{engine.height}", 'yellow')}")

# Set the frame rate to x frames per second:
engine.set_fps(30)

# TITLES
game_title = "space typer"
subtitle_choices = ["Spacewar!", "Computer Space", "space bar war", "star wars", "star trek", "The Hitchhikers Guide to the Galaxy", "Star Citizen", "No Man`s Sky", "Elite Dangerous!", "starfield"]
subtitle = random.choice(subtitle_choices)

# SCORES
total_score               = 0 # your max score per game, it saves current value if current is bigger your end score
current_score             = 0 # the current_score, if it's <= 0, it's game over, time bites on this value so be careful

total_right_words_score   = 0
total_right_letters_score = 0
total_wrong_words_score   = 0
total_wrong_letters_score = 0

score_right_words         = 0
score_right_letters       = 0
score_wrong_words         = 0
score_wrong_letters       = 0
save_score_wrong_letter   = 0


# WORDS
custom_word_collection = list() # when 'preset difficulty' is custom,
# ¬ 'preset difficulty' isn't a variable in this script, it is just difficulty
append_custom_word     = str()  # when adding your own word's libraries addon stuff
main_word_collection   = set()  # contains all the words that can be shown when playing
active_words           = list() # the active words when playing that are visible, and interactable when playing
active_words_positions = list() # the positions of all the words in the game

max_words              = 10000  # the maximum amount of allowed words, limits memory usage a tiny little bit
# word_fall_speed      = 1 * (engine.height / (general_scale * aspect_ratio[1])) #perf
word_fall_speed        = 0.5 * (engine.height / (general_scale * aspect_ratio[1]))
                                # the speed of the word falling down, (generals scale and aspect ratio are constants)
# ¬ it is responsive depending on the engine's height, in order to give the player the same time to type the whole word
# - so a player with a smaller screen wil not have disadvantages when playing
# word_fall_speed_max    = 1.333 * word_fall_speed # is bigger than 'word fall speed', because it is the maximum speed #perf
word_fall_speed_max    = 1.666 * word_fall_speed # is bigger than 'word fall speed', because it is the maximum speed
# word_speed_increase    = 0.001  # adds to 'word generate speed' and 'word fall speed' per second, when playing #perf
word_speed_increase    = 0.002  # adds to 'word generate speed' and 'word fall speed' per second, when playing
# word_generate_speed    = 3 + 3 * word_speed_increase #perf
word_generate_speed    = 2 + 2 * word_speed_increase
                                # the speed, how fast a word gets generated per second, it varies for every difficulty
# ¬ to count down properly before starting

difficulty             = "normal" # default active difficulty
suggest_difficulty     = random.choice(word_collections.difficulty_collection_titles)
                                  # suggests a difficulty as an extra on the first menu


# KEYBOARD input variables
target_key  = str() # your imputed key
save_key    = str() # your previously imputed key
target_word = -1    # the word you are typing, if -1, no word locked

# COUNTERS
frames_counter       = 0          # counts the frames from the start of running the game
play_clock           = [0, 0, 0]  # a collection containing play_counter_, -hour, -min and - sec
converted_clock      = [0, 0, 0]  # a converted selection to overcome value overwrites, this is used to draw to screen
play_total_time      = [0, 0, 0]  # the total amount of hours, minutes and seconds that you played, are not rounded
play_counter_hour    = 0          # counts your played hours,   they act like a clock, has no stop
play_counter_min     = 0          # counts your played minutes, they act like a clock, 60 minutes will become 1 hour
play_counter_sec     = 0          # counts your played seconds, they act like a clock, 60 seconds will become 1 minute
play_counter_sec_fps = 0          # counts your played frames,  they act like a clock, fps frames will become 1 second
play_counter_sec_max = engine.fps # resets counter frames when exactly 1 second added, in order to add a second
play_word_counter    = 0          # indicates how many words are played


# MUSIC
play_music = False                                        # when false, no sound, no music
                                                          # when true, engine is allowed to play sound and music
# pygame.mixer_music.load("resources/music/game_music.wav") # loads the game music in


# VIEWPORT ENGINE
background_color    = (0, 0, 0) # the background 3 rgb channels of your game, is transparent for a cool fade effect
background_opacity  = 1         # the background alpha channel  of your game, is transparent for a cool fade effect

small_viewport_edge = None      # the smallest viewport edge of your engine
large_viewport_edge = None      # the largest  viewport edge of your engine
# checks what the 2 variables above are and assigns them there correct value's
if aspect_ratio[0] > aspect_ratio[1]: # if width bigger than height
    small_viewport_edge = engine.height
    large_viewport_edge = engine.width
    common.print_info(f">>> {colors.get_colored_text("LANDSCAPE", 'yellow', )}")
elif aspect_ratio[0] < aspect_ratio[1]: # if height bigger than width
    small_viewport_edge = engine.width
    large_viewport_edge = engine.height
    common.print_info(f">>> {colors.get_colored_text("PORTRAIT", 'yellow', )}")
else: # square display
    small_viewport_edge = (engine.width + engine.height) / 2
    large_viewport_edge = (engine.width + engine.height) / 2

center_X = engine.width / 2
center_Y = engine.height / 2


# PLAYER
player_image_collection       = list() # will contain all player rotation images per degree
player_image                  = None   # will contain only the active player image

# IMAGE LIBRARY SPACE SHIP
image_collection_loaded_index = 0      # loading index of your image collection
image_collection_init_done    = False  # turns true after you write loading on the screen
image_collection_loaded_all   = False  # turns true after all your images in your sequence are loaded
image_collection_path         = "spaceship/"
                                       # the path whit out file naming
image_collection_filename     = "ship" # the file naming without extension
image_collection_extension    = "png"  # the extensions of the files
image_collection_prefix       = False  # if the sequence number is prefix, turn true, turn suffix false
image_collection_suffix       = False  # if the sequence number is suffix, turn true, turn prefix false
image_collection_start        = 0      # total sequence scope start
image_collection_stop         = 180    # total sequence scope stop
# image_collection_step         = 1      # total sequence scope step #perf
image_collection_step         = 5      # total sequence scope step
image_collection_qty          = 5      # sequence scope step quantity, makes it possible to draw a loading screen

player_angle                  = float() # in deg
player_angle_converted        = int()   # is used for indexing
player_angle_rounded          = int()   # angle rounded to 1, to visualize
# ¬ this happens to be the same, but if you want to rotate around 5 degrees for every frame, these make sense
player_current_angle          = 90      # standard player angle

player_size = large_viewport_edge / 5                          # the size of the player
player_position_X = center_X                                   # the center point X value of the player
player_position_Y = engine.height - player_size / 3 * 2        # the center point Y value of the player
player_direction  = (player_position_X, player_position_Y - 1) # vectors

# player_vectors
player_dot_vector_scaler        = large_viewport_edge / 3
player_dot_vector               = (player_position_X, player_position_Y, player_position_X + player_dot_vector_scaler, player_position_Y)
player_dot_unit_vector          = tuple()
player_dot_vector_length        = large_viewport_edge / 3
player_normalized_dot_vector    = tuple()

player_mouse_vector             = (player_position_X, player_position_Y, player_position_X, player_position_Y - 1)
player_mouse_unit_vector        = tuple()
player_mouse_vector_length      = float()
player_normalized_mouse_vector  = (0, 1)

player_letter_vector            = (player_position_X, player_position_Y, player_position_X, player_position_Y - 1)
player_letter_unit_vector       = tuple()
player_letter_vector_length     = float()
player_normalized_letter_vector = (0, 1)

# BULLETS EN FLARES
# BULLETS (letter mining) & (firring missiles)
# ¬ used for esthetics the special effects makes the game more interesting
# ¬ bullets are used when playing and left-clicking,
# - you fire a very dark purple bullet to the direction of your cursor at the time of clicking
bullet_direction          = tuple() # the target of a bullet
bullet_unit_vector        = tuple() # the vector towards the bullet's target, vector is just 2 coördinates
bullet_vector_length      = tuple() #
bullet_normalized_vector  = tuple() #

bullet_speed              = 3       # the speed, scaler of velocity

bullet_converted_vector   = list()  # collection of the vectors per bullet
bullet_converted_velocity = list()  # collection of bullets normalized vectors with length of bullet speed
bullet_color              = list()  # collection of collors per bullet

# FLARE (letter losing)
flare_direction           = tuple()
flare_unit_vector         = tuple()
flare_vector_length       = tuple()
flare_normalized_vector   = tuple()

flare_speed               = 3 # the speed
flare_duration            = 0.3 * engine.fps

flare_points_collection   = list()
flare_timer               = list()

flare_converted_vector    = list()
flare_converted_velocity  = list()
flare_color               = list()

projectile_size = 5

# stars
stars_amount = 75
star_size = 2
star_positions = ([0, 0],)
stars_xPositions_list = []
stars_yPositions_list = []
stars_direction = [-1, -1]
stars_speed = 1


# MENU
# » loading
loading = False
loading_time = 0

# » main
menu_main_image         = engine.load_image("menu/menu_main.png")
# » outer
menu_outer_image        = engine.load_image("menu/menu_outer.png")
# » side
menu_side_light_image   = engine.load_image("menu/menu_S_light.png")
menu_side_neutral_image = engine.load_image("menu/menu_S_neutral.png")
menu_side_normal_image  = engine.load_image("menu/menu_S_normal.png")
menu_side_dark_image    = engine.load_image("menu/menu_S_dark.png")
# » top
menu_top_light_image    = engine.load_image("menu/menu_T_light.png")
menu_top_neutral_image  = engine.load_image("menu/menu_T_neutral.png")
menu_top_normal_image   = engine.load_image("menu/menu_T_normal.png")
menu_top_dark_image     = engine.load_image("menu/menu_T_dark.png")

menu_size                      = large_viewport_edge * 0.9
menu_outer_animation_scale     = 1   # the outer layer animated scale factor, for a scale animation effect
menu_outer_animation_direction = "+" # indicates if it has to expand or shrink
menu_top_animation_scale       = 1   # the top highlight layer animated scale factor, for a scale animation effect,
# # ¬ only scales on the X axes
menu_top_animation_direction   = "+" # indicates if it has to expand or shrink


# BUTTONS
# small buttons
# » normal
button_small =               engine.load_image("buttons/button_S.png")
button_small_blue =          engine.load_image("buttons/button_S_blue.png")
button_small_green =         engine.load_image("buttons/button_S_green.png")
button_small_red =           engine.load_image("buttons/button_S_red.png")
button_small_purple =        engine.load_image("buttons/button_S_purple.png")
button_small_orange =        engine.load_image("buttons/button_S_orange.png")
# » hover
button_small_hover =         engine.load_image("buttons/button_S_H.png")
button_small_blue_hover =    engine.load_image("buttons/button_S_blue_H.png")
button_small_green_hover =   engine.load_image("buttons/button_S_green_H.png")
button_small_red_hover =     engine.load_image("buttons/button_S_red_H.png")
button_small_purple_hover =  engine.load_image("buttons/button_S_purple_H.png")
button_small_orange_hover =  engine.load_image("buttons/button_S_orange_H.png")
# medium buttons
# » normal
button_medium =              engine.load_image("buttons/button_M.png")
button_medium_blue =         engine.load_image("buttons/button_M_blue.png")
button_medium_green =        engine.load_image("buttons/button_M_green.png")
button_medium_red =          engine.load_image("buttons/button_M_red.png")
button_medium_purple =       engine.load_image("buttons/button_M_purple.png")
button_medium_orange =       engine.load_image("buttons/button_M_orange.png")
# » hover
button_medium_hover =        engine.load_image("buttons/button_M_H.png")
button_medium_blue_hover =   engine.load_image("buttons/button_M_blue_H.png")
button_medium_green_hover =  engine.load_image("buttons/button_M_green_H.png")
button_medium_red_hover =    engine.load_image("buttons/button_M_red_H.png")
button_medium_purple_hover = engine.load_image("buttons/button_M_purple_H.png")
button_medium_orange_hover = engine.load_image("buttons/button_M_orange_H.png")
# big buttons
# » normal

# custom buttons
# difficulty
# » normal
button_difficulty =          engine.load_image("buttons/difficulty.png")
# » hover
button_difficulty_hover =    engine.load_image("buttons/difficulty_H.png")
# » extra's
button_card_easy =           engine.load_image("buttons/easy_card.png")
button_card_normal =         engine.load_image("buttons/normal_card.png")
button_card_hard =           engine.load_image("buttons/hard_card.png")
button_card_extreme =        engine.load_image("buttons/extreme_card.png")
button_card_custom =         engine.load_image("buttons/custom_card.png")

# custom word input
input_custom_word_image =    engine.load_image("buttons/custom_input.png")


# BUTTON / ICON positions
# the object_mode == CENTER
# buttons
# on START
start_button_left = engine.width / 2 - 15 * viewport_scaler
start_button_top = engine.height - 30 * viewport_scaler
start_button_width = 30 * viewport_scaler
start_button_height = 30 * viewport_scaler


# in MENU's
button_up = menu_size / 1.57
button_down = menu_size / 1.4

justify_text_left = engine.width / 3.7
justify_text_right = engine.width - justify_text_left

menu_button_margin = 10
menu_button_width = 60 * viewport_scaler
button_height = (menu_button_width * 1.135)
justify_button_left = (engine.width / 2) - (engine.width / 4 / 2) - 11.25 * viewport_scaler
justify_button_right = (engine.width / 2) + (engine.width / 4 / 2) + 11.25 * viewport_scaler

hover_difficulty_button = False
difficulty_Y = (menu_size / 1.57 + (button_up - button_height)) / 2
difficulty_height = (menu_button_width * 1.135) * 2

long_button_width = (menu_size / 3.5 - menu_button_width) * 2 + menu_button_margin * 11.25 * viewport_scaler
medium_button_width = menu_size / 3 - menu_button_margin - menu_button_width
small_button_width = button_height

card_scaler = 1

card_smalling = 0.8
card_hover_smalling = 0.9
card_position_smalling = 1 - (1 + card_smalling) / 2
card_hover_position_smalling = 1 - (1 + card_hover_smalling) / 2

card_size = 0.98 * card_scaler
partial_width = long_button_width / 5.2
cards_max_Y = button_up - button_height * card_size
cards_position_Y = button_up


# icon positions
icon_L_left = large_viewport_edge // 5
icon_L_top = engine.height // 2
icon_R_left = engine.width - large_viewport_edge // 5
icon_R_top = engine.height // 2
icon_size = large_viewport_edge


# ICONS
icon_left = engine.load_image("icons/arrow_left.png")
icon_right = engine.load_image("icons/arrow_right.png")
animation_play_size = 1
animation_play_direction = "+"


# ANIMATIONS
background_transition_alpha = 1
transition_in = False
transition_out = True


# TESTING
testing_dot_vector = (player_position_X, player_position_Y, player_position_X + 1 * player_dot_vector_scaler, player_position_Y)
testing_mouse_vector = (player_position_X, player_position_Y, engine.mouse_x, engine.mouse_y)
test_print_update_counter = 0

# IMAGE loader function              collection_scope: tuple = (0, 1),
def prepare_image_sequence(path_type: str = "R", fix_position: str = "SUF") -> tuple:
    """
    loads a certain amount of images

    :param: path, ONLY FOLDERS towards file location, the FILE itself is NOT INCLUDED, end parameter with "/".
    example:    "../content/images/".
    standard:   "../resources/images/".

    :param path_type: relative / absolute path, it will recognise it by itself.
    standard:   "R" ==» "relative"
    status: in the work

    :param fix_position: the location of where the image number will be added to the filename.
    example:    "PRE" / "SUF" »»» "photo1.img" / "1photo.img"
    standard:   "SUF" ==» "suffix"

    :return: tuples with images
    """
    global image_collection_loaded_all
    global image_collection_path, image_collection_filename, image_collection_extension
    global image_collection_prefix, image_collection_suffix
    global image_collection_start, image_collection_stop, image_collection_step

    common.print_info("\n", f"{colors.get_colored_text("===== " * 5, 'light gray')}", sep="")
    common.print_info(f"loading image collection {colors.get_colored_text("info", 44)}")

    # DIRECTORY_PATH
    # checks if directory_path ends with '/'.
    if not (image_collection_path[len(image_collection_path) - 1] == "/"):
        image_collection_path += "/"
    common.print_info(f"path: \t\t{colors.get_colored_text(f"{image_collection_path[:-1]}", 'light blue')}/", end="")
    if image_collection_path.find("../"):
        path_type = "R" # relative path


    # FILENAME
    # checks if filename contains '.'.
    if (image_collection_filename.find(".")) >= 0:
        image_collection_filename = image_collection_filename.replace(".", "")
    common.print_info(f"{colors.get_colored_text(f"{image_collection_filename}", 'blue')}", end="")


    # EXTENSIONS
    # checks if extensions contains '.'.
    if (image_collection_extension.find(".")) >= 0:
        image_collection_extension = image_collection_extension.replace(".", "")
    common.print_info(f".{colors.get_colored_text(f"{image_collection_extension}", 'light blue')}")

    # checks if extensions are supported
    supported_extensions = ("png", "jpg", "jpeg")
    if not image_collection_extension in supported_extensions:
        common.print_error("parameter input", "load_image_collection(", ")", "extensions", True)

    image_collection_stop += 1 # stop correction for the for loops


    # PATH TYPE
    path_type = path_type.upper()
    # checks if path_type is RELATIVE or ABSOLUTE
    if path_type == "R":
        common.print_info(f"type: \t\t{colors.get_colored_text("relative", 'light gray')}")
    elif path_type == "A":
        common.print_info(f"type: \t\t{colors.get_colored_text("absolute", 'light gray')}")
    else:
        common.print_error("parameter input", "load_image_collection(", ")", "path_type", True)
        pass # temporary

    # FIX POSITION
    # checks if fix_position is PREFIX or SUFFIX
    if fix_position == "PRE":
        image_collection_prefix = True
        image_collection_suffix = False
        common.print_info(f"position: \t{colors.get_colored_text("prefix", 'dark gray')}\n")
    elif fix_position == "SUF":
        image_collection_prefix = False
        image_collection_suffix = True
        common.print_info(f"position: \t{colors.get_colored_text("suffix", 'dark gray')}\n")
    else:
        common.print_error("parameter input", "load_image_collection(", ")", "path_type", True)
        pass # temporary

    common.print_info(f"start {colors.get_colored_text("loading images", 44)} in to collection: ")

def load_image_sequence() -> bool:
    """
    this function loads images

    :return:
    """
    global player_image_collection
    global image_collection_loaded_index

    # IMAGE COLLECTION MAKER
    img_counter = 0
    for counter in range(image_collection_start + image_collection_loaded_index, image_collection_stop, image_collection_step):
        if image_collection_prefix:   complete_path = f"{image_collection_path}{counter}{image_collection_filename}.{image_collection_extension}"
        elif image_collection_suffix: complete_path = f"{image_collection_path}{image_collection_filename}{counter}.{image_collection_extension}"
        common.print_info(f"['\033[94m{complete_path}\033[0m']")
        load_image = engine.load_image(f"{complete_path}")
        player_image_collection.append(load_image)
        #update screen not possible?
#        engine.draw_text(f"{counter}", 20, 20)
#         image_collection_loaded_index = counter + 1 #perf
        image_collection_loaded_index = counter + 5
        # img_counter += 1 #perf
        img_counter += 5
        if img_counter >= image_collection_qty :
            break
    return image_collection_loaded_index > image_collection_stop - 1

# CHECK functions
def check_engine_border(pos_x: float, pos_y: float) -> tuple:
    """
    checks if parameters top, left, bottom & right are inside the engine's screen

    :param pos_x: for left and right border checking
    :param pos_y: for top and bottom border checking

    :return: tuples of 4 booleans that indicates if is within engine borders
    """

    if pos_y <= 0:
        top_condition = False
    else:
        top_condition = True

    if pos_x <= 0:
        left_condition = False
    else:
        left_condition = True

    if pos_y >= engine.height:
        bottom_condition = False
    else:
        bottom_condition = True

    if pos_x >= engine.width:
        right_condition = False
    else:
        right_condition = True

    return (top_condition, left_condition, bottom_condition, right_condition)

# here were calc functions

def start_game_music():
    """
    starts the game music

    :return:
    """
    global play_music

    # if not play_music:
    #     pygame.mixer_music.set_volume(0.05)
    #     pygame.mixer_music.play(loops=-1, fade_ms=200)
    pass

def stop_game_music():
    """
    stops the game music

    !!!!! you can't stop it by clicking on the close arrow button,
    the music will stop eventually.
    :return:
    """
    # global play_music
    #
    # if play_music:
    #     play_music = False
    #     pygame.mixer_music.fadeout(1000)
    pass

# CURSOR
def draw_cursor(color: tuple = (1, 1, 1)):
    engine.shape_mode = ShapeMode.CENTER

    engine.outline_color = color
    engine.color = None

    engine.draw_circle(engine.mouse_x, engine.mouse_y, 20, 2)
    engine.draw_line(engine.mouse_x - 2, engine.mouse_y - 2, engine.mouse_x - 10, engine.mouse_y - 10, 2)
    engine.draw_line(engine.mouse_x + 5, engine.mouse_y - 5, engine.mouse_x + 10, engine.mouse_y - 10, 2)
    engine.draw_line(engine.mouse_x - 7, engine.mouse_y + 7, engine.mouse_x - 10, engine.mouse_y + 10, 2)

# SCORE functions
def draw_score():
    """
    draw's a player stats image

    :return: player image
    """
    global converted_clock

    engine.shape_mode = ShapeMode.CENTER

    engine.set_font(fonts.mono_font)
    engine.set_font_size(fonts.normal_text_size)

    position_Y = (player_position_Y + player_size / 3) - fonts.normal_text_size

    left = (player_position_X - player_size / 2) * 0.25
    right = engine.width - ((player_position_X - player_size / 2) * 0.25)
    center_left = (player_position_X - player_size / 2) * 0.8
    center_right = engine.width - ((player_position_X - player_size / 2) * 0.8)

    title_right = "right"
    title_wrong = "wrong"
    title_timer = "timer"
    title_score = "score"

    correct_words =     f"W. {score_right_words}"
    correct_letters =   f"L. {score_right_letters}"
    lost_words =        f"W. {score_wrong_words}"
    incorrect_letters = f"L. {score_wrong_letters}"

    score =             f"{round(current_score, 2)}"
    top_score =         f"{round(total_score, 2)}"
    score_decoration =  f"-= {" " * 6} =-" # start value

    converted_clock = [f"{play_clock[0]}", f"{play_clock[1]}", f"{play_clock[2]}"]
    if len(converted_clock[0]) < 2: converted_clock[0] = f"0{converted_clock[0]}"
    if len(converted_clock[1]) < 2: converted_clock[1] = f"0{converted_clock[1]}"
    if len(converted_clock[2]) < 2: converted_clock[2] = f"0{converted_clock[2]}"
    text_clock =        f"{converted_clock[0]}:{converted_clock[1]}:{converted_clock[2]}"
    text_timer =        f"{play_total_time[0]} {play_total_time[1]} {play_total_time[2]}"
    # hour =              f"H. {play_total_time[0]}"
    # min =               f"M. {play_total_time[1]}"
    # sec =               f"S. {play_total_time[2]}"

    length_correct_words = len(correct_words) * fonts.normal_text_size * 0.6
    length_correct_letters = len(correct_letters) * fonts.normal_text_size * 0.6
    length_lost_words = len(lost_words) * fonts.normal_text_size * 0.6
    length_incorrect_letters = len(incorrect_letters) * fonts.normal_text_size * 0.6

    top_score_separated = top_score.split(".")

    # change top score
    # change top score BEFORE the dot
    if len(top_score_separated[0]) == 1: top_score = str("  " + top_score)
    if len(top_score_separated[0]) == 2: top_score = str(" " + top_score)
    # change top score AFTER the dot
    if not len(top_score_separated) == 2: top_score = str(top_score.split(".")[0] + "." + "00")
    elif len(top_score_separated[1]) == 1: top_score = str(top_score.split(".")[0] + "." + top_score.split(".")[1] + "0")

    if len(top_score_separated) == 2:
        length_left_top_score = len(top_score_separated[0]) * fonts.normal_text_size * 0.6
        length_right_top_score = len(top_score_separated[1]) * fonts.normal_text_size * 0.6
        score_decoration = f"-= {" " * len(top_score)} =-"

    score_separated = score.split(".")

    # change score BEFORE the dot
    if len(score_separated[0]) == 1: score = str("  " + score)
    if len(score_separated[0]) == 2: score = str(" " + score)
    # change score AFTER the dot
    if not len(score_separated) == 2: score = str(score.split(".")[0] + "." + "00")
    elif len(score_separated[1]) == 1: score = str(score.split(".")[0] + "." + score.split(".")[1] + "0")

    if len(score_separated) == 2:
        length_left_score = len(score_separated[0]) * fonts.normal_text_size * 0.6
        length_right_score = len(score_separated[1]) * fonts.normal_text_size * 0.6

    length_score = len(score) * fonts.normal_text_size * 0.6
    add_left_score = 3 * fonts.normal_text_size * 0.6


    length_clock = len(text_clock) * fonts.normal_text_size * 0.6
    length_timer = len(text_timer) * fonts.normal_text_size * 0.6
    # length_hour = len(hour) * fonts.normal_text_size * 0.6
    # length_min = len(min) * fonts.normal_text_size * 0.6
    # length_sec = len(sec) * fonts.normal_text_size * 0.6

    # titles
    engine.color = 0.5, 0.5, 0.5
    engine.draw_text(f"{title_right}", left, position_Y, False)
    engine.draw_text(f"{title_wrong}", center_left - (5 * fonts.normal_text_size * 0.6), position_Y, False)
    engine.draw_text(f"{title_score}", center_right, position_Y, False)
    engine.draw_text(f"{title_timer}", right - (5 * fonts.normal_text_size * 0.6), position_Y, False)

    position_Y += fonts.normal_text_size

    # correct words
    engine.color = colors.green
    engine.draw_text(f"{correct_words}", left, position_Y, False)

    position_Y += fonts.normal_text_size

    # correct letters
    engine.color = colors.l_green
    engine.draw_text(f"{correct_letters}", left, position_Y, False)

    position_Y -= fonts.normal_text_size

    # lost words
    engine.color = colors.red
    engine.draw_text(f"{lost_words}", center_left - length_lost_words, position_Y, False)

    position_Y += fonts.normal_text_size

    # incorrect letters
    engine.color = colors.l_red
    engine.draw_text(f"{incorrect_letters}", center_left - length_incorrect_letters, position_Y, False)

    position_Y -= fonts.normal_text_size

    # total score
    engine.color = colors.orange
    engine.draw_text(f"{top_score}", center_right + add_left_score, position_Y, False)
    engine.draw_text(f"{score_decoration}", center_right, position_Y, False)

    position_Y += fonts.normal_text_size

    # current score
    engine.color = colors.l_orange
    engine.draw_text(f"{score}", center_right + add_left_score, position_Y, False)

    position_Y -= fonts.normal_text_size

    # clock
    engine.color = colors.l_purple1
    engine.draw_text(f"{text_clock}", right - length_clock, position_Y, False)

    position_Y += fonts.normal_text_size

    # timer
    engine.color = colors.l_purple2
    engine.draw_text(f"{text_timer}", right - length_timer, position_Y, False)

    # engine.draw_text(f"{hour}", center_right, position_Y, False)
    #
    # center_inbetween = ((center_right + length_hour + right - length_sec) / 2) - length_min / 2
    # engine.draw_text(f"{min}", center_inbetween, position_Y, False)
    #
    # engine.draw_text(f"{sec}", right - length_sec, position_Y, False)


    position_Y -= fonts.normal_text_size
def calc_score():
    """
    calculates the TOTAL score displayed orange if you play the game

    :return: the total score
    """
    global game_state
    global current_score, total_score
    global total_right_words_score, total_right_letters_score, total_wrong_words_score, total_wrong_letters_score
    global converted_clock

    # # CHECKPOINT
    # # NOG NIET KLAAR
    score_scaler = 1

    # # score difficulty factors
    if difficulty   == "easy":    score_scaler = 2.5
    elif difficulty == "normal":  score_scaler = 2
    elif difficulty == "hard":    score_scaler = 1.5
    elif difficulty == "extreme": score_scaler = 1
    elif difficulty == "custom":  score_scaler = 1

    current_score = (score_right_words + (score_right_letters / 10)) - ((score_wrong_words + (score_wrong_letters / 5)) * score_scaler) - (play_total_time[2] / 3)

    current_right_words_score   = score_right_words
    current_right_letters_score = score_right_letters
    current_wrong_words_score   = score_wrong_words
    current_wrong_letters_score = score_wrong_letters

    # highscore per game
    if current_score               > total_score:               total_score               = current_score
    if current_right_words_score   > total_right_words_score:   total_right_words_score   = current_right_words_score
    if current_right_letters_score > total_right_letters_score: total_right_letters_score = current_right_letters_score
    if current_wrong_words_score   > total_right_words_score:   total_wrong_words_score   = current_wrong_words_score
    if current_wrong_letters_score > total_right_letters_score: total_wrong_letters_score = current_wrong_letters_score

    # GAME OVER! when current score == 0 only after 1 minute of playtime
    if current_score < 0 and play_total_time[1] >= 1:
        engine.set_font(fonts.strong_font)
        engine.set_font_size(large_viewport_edge // 20)

        engine.color = colors.red

        engine.shape_mode = ShapeMode.CENTER

        engine.draw_text("GAME OVER!", center_X, center_Y, True)
        freeze_game_over = 120
        game_over_condition = True

        if  converted_clock[1] == 60: # if minutes are 60
            converted_clock[1]  = 0   # minutes to 0
            converted_clock[0] += 1   # add 1 hour
        if  converted_clock[2] == 60: # if seconds are 60
            converted_clock[2]  = 0   # seconds to 0
            converted_clock[1] += 1   # add 1 minute

        # from PLAY to RESULT screen
        game_state = GameState.RESULT

# DIFFICULTY functions
def setup_difficulty():
    """
    if the user pressed start, it will check the difficulty the user wants to play, and adapt the game to the chosen difficulty

    :return: applied difficulty
    """
    global main_word_collection
    global word_generate_speed, word_fall_speed, word_fall_speed_max

    if difficulty == "easy":
        main_word_collection.clear()
        main_word_collection.update(fonts.lowercase_variables(word_collections.easy_word_collection))

        word_generate_speed += 1
        word_fall_speed *= 0.75
        word_fall_speed_max = 2

        common.print_info("start game difficulty on:", colors.get_colored_text("easy", "green"))

    elif difficulty == "normal":
        main_word_collection.clear()
        main_word_collection.update(fonts.lowercase_variables(word_collections.easy_word_collection))
        main_word_collection.update(fonts.lowercase_variables(word_collections.normal_word_collection))

        word_generate_speed += 0
        word_fall_speed *= 1
        word_fall_speed_max = 1.75

        common.print_info("start game difficulty on:", colors.get_colored_text("normal", "blue"))

    elif difficulty == "hard":
        main_word_collection.clear()
        main_word_collection.update(fonts.lowercase_variables(word_collections.easy_word_collection))
        main_word_collection.update(fonts.lowercase_variables(word_collections.normal_word_collection))
        main_word_collection.update(fonts.lowercase_variables(word_collections.hard_word_collection))

        word_generate_speed += 0
        word_fall_speed *= 1.1
        word_fall_speed_max = 1.5

        common.print_info("start game difficulty on:", colors.get_colored_text("hard", "orange"))

    elif difficulty == "extreme":
        main_word_collection.clear()
        main_word_collection.update(fonts.lowercase_variables(word_collections.easy_word_collection))
        main_word_collection.update(fonts.lowercase_variables(word_collections.normal_word_collection))
        main_word_collection.update(fonts.lowercase_variables(word_collections.hard_word_collection))
        main_word_collection.update(fonts.lowercase_variables(word_collections.extreme_word_collection))

        word_generate_speed += 0
        word_fall_speed *= 0.9
        word_fall_speed_max = 1.25

        common.print_info("start game difficulty on:", colors.get_colored_text("extreme", "red"))

    elif difficulty == "custom":
        if len(custom_word_collection) == 0:
            main_word_collection.add("pew")
        main_word_collection.update(custom_word_collection)

        word_generate_speed += 1
        word_fall_speed *= 0.5
        word_fall_speed_max = word_collections.custom_word_fall_speed_max

        common.print_info("start game difficulty on:", colors.get_colored_text("custom", "magenta"))

def add_custom_word(key: str or bool = False):
    """
    draw's your word when typing your word,
    this function also adds the custom word to the collection

    :param key: the key for adding a letter to string

    :return:
    """
    global main_word_collection, difficulty, custom_word_collection, append_custom_word

    # locals
    modify_fall_speed = False
    modify_generate_speed = False

    # run only if the user clicks at custom game mode in the MENU state
    if difficulty == "custom":
        # allowed characters
        allowed_characters = (" ", "-", "'", "`", ".")
        numbers = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")
        allowed_characters = set(allowed_characters)
        allowed_characters.update(numbers)
        allowed_characters = tuple(allowed_characters)

        if type(key) != bool and (len(key) == 1 and key.isalpha()) or (key in allowed_characters):
            append_custom_word += key
        elif key == "BACKSPACE": # remove 1 character
            append_custom_word = append_custom_word[:-1] # keep every letter accept the last one
        elif key == "ENTER" or key == True: # COMMITS ACTION

            # checks if you want to RESET or CLEAR
            if append_custom_word == "reset" or append_custom_word == "clear":
                custom_word_collection.clear()
                main_word_collection.clear()

            # checks if you want to ADD a whole LIBRARY
            # first condition
            elif  append_custom_word in word_collections.difficulty_collection_titles:

                # IF EASY
                if append_custom_word.strip().lower() == "easy":
                    for index in range(len(word_collections.easy_word_collection)):
                        custom_word_collection.append(word_collections.easy_word_collection[index].strip().lower())


                # IF NORMAL
                elif append_custom_word.strip().lower() == "normal":
                    for index in range(len(word_collections.normal_word_collection)):
                        custom_word_collection.append(word_collections.normal_word_collection[index].strip().lower())

                # IF HARD
                elif append_custom_word.strip().lower() == "hard":
                    for index in range(len(word_collections.hard_word_collection)):
                        custom_word_collection.append(word_collections.hard_word_collection[index].strip().lower())

                # IF EXTREME
                elif append_custom_word.strip().lower() == "extreme":
                    for index in range(len(word_collections.extreme_word_collection)):
                        custom_word_collection.append(word_collections.extreme_word_collection[index].strip().lower())

                # IF CUSTOM: you cant add custom library, so instead add the most special word all times!
                # the answer to the questions of life, the universe and everything else
                elif append_custom_word.strip().lower() == "custom":
                    custom_word_collection.append("42".strip().lower())

            elif append_custom_word in word_collections.get_easter_eggs():
                for collection_name in word_collections.get_easter_eggs():
                    if collection_name == append_custom_word:
                        break

                for word in word_collections.get_easter_egg(collection_name):
                    custom_word_collection.append(word.strip().lower())

            # # set custom fall SPEED
            # elif   (append_custom_word.split("fall speed")[1].strip().isnumeric() and float(append_custom_word.split("fall speed")[1].strip()) > 0) \
            #     or (append_custom_word.split("fallspeed")[1].strip().isnumeric()  and float(append_custom_word.split("fallspeed")[1].strip()) > 0):
            #
            #     modify_fall_speed = True
            #
            #     if append_custom_word.split("fall speed")[0].strip():
            #         append_custom_word.split("fall speed")[0].strip().replace(" ", "")
            #
            #     word_collections.custom_word_fall_speed = float(append_custom_word.split("fallspeed")[1].strip())
            #     word_collections.custom_word_fall_speed_max = float(append_custom_word.split("fallspeed")[1].strip())
            #
            # # if set custom fall speed, you can set custom fall speed MAX
            # elif modify_fall_speed and \
            #        ((append_custom_word.split("fall speed max")[1].strip().isnumeric() and int(append_custom_word.split("fall speed max")[1].strip()) > 0) \
            #     or  (append_custom_word.split("fallspeedmax")[1].strip().isnumeric()   and int(append_custom_word.split("fallspeedmax")[1].strip()) > 0)) \
            #     and (word_collections.custom_word_fall_speed <= int(append_custom_word.split("fall speed max")[1].strip()) > 0):
            #
            #     if append_custom_word.split("fall speed max")[0].strip():
            #         append_custom_word.split("fall speed max")[0].strip().replace(" ", "")
            #
            #     word_collections.custom_word_fall_speed = int(append_custom_word.split("fallspeedmax")[1].strip())
            #
            # # set custom word generate speed
            # elif   (append_custom_word.split("generate speed")[1].strip().isnumeric() and float(append_custom_word.split("generate speed")[1].strip()) > 0) \
            #     or (append_custom_word.split("generatespeed")[1].strip().isnumeric() and float(append_custom_word.split("generatespeed")[1].strip()) > 0):
            #
            #     modify_generate_speed = True
            #
            #     if append_custom_word.split("generate speed")[0].strip():
            #         append_custom_word.split("generate speed")[0].strip().replace(" ", "")
            #
            #     word_collections.custom_word_generate_speed = float(append_custom_word.split("fall speed")[1].strip())

            # IF WORD, no special easter eggs
            elif append_custom_word.strip().lower().isalnum() \
                or append_custom_word.strip().lower().replace(str(allowed_characters[0]), "A").isalnum() \
                or append_custom_word.strip().lower().replace(str(allowed_characters[1]), "B").isalnum() \
                or append_custom_word.strip().lower().replace(str(allowed_characters[2]), "C").isalnum() \
                or append_custom_word.strip().lower().replace(str(allowed_characters[3]), "D").isalnum() \
                or append_custom_word.strip().lower().replace(str(allowed_characters[4]), "E").isalnum():
                custom_word_collection.append(append_custom_word.strip().lower())

            if not modify_fall_speed and not modify_generate_speed:
                append_custom_word = ""

                sound.play_note("sol+", 5, 8)
                common.print_info(custom_word_collection)
                common.print_info("main_word_collection", type(main_word_collection))
                common.print_info("custom_word_collection", type(custom_word_collection))
                main_word_collection.update(fonts.lowercase_variables(custom_word_collection))

                common.print_info(main_word_collection)

def textarea_custom_word_input():
    """
    if in options menu, the difficulty is set to custom, you have to be able to add custom words
    this function does that,
    the UI does not get changed in this function but in the OPTIONS function

    :return: -
    """
    engine.set_font(fonts.strong_font)
    engine.set_font_size(fonts.heading_text_size)

    engine.shape_mode = ShapeMode.CENTER

    if append_custom_word == "reset" or append_custom_word == "clear": engine.color = colors.red[0], colors.red[1], colors.red[2]
    elif append_custom_word in word_collections.difficulty_collection_titles: engine.color = colors.blue[0], colors.blue[1], colors.blue[2]
    elif append_custom_word in word_collections.get_easter_eggs(): engine.color = colors.orange[0], colors.orange[1], colors.orange[2]
    # CHECKPOINT B
    else: engine.color = 1, 1, 1
    whitespace = large_viewport_edge / 600

    # draw text area
    input_custom_word_image.draw_fixed_size(center_X, engine.height / 1.55, long_button_width / 16 * 15, button_height, True)

    # draw's text
    # engine.set_font(fonts.mono_font)
    engine.draw_text(append_custom_word.upper(), engine.width / 3.7, engine.height / 1.61, False)

    # draw's cursor when hovering over + button to add custom word
    # if engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, #perf
    #     engine.width * 0.718, engine.height / 1.575, small_button_width // 5 * 4, button_height // 5 * 4): #perf
    #     draw_cursor() #perf

# PLAYER functions
def draw_player():
    """
    draws a player
    :return: -
    """
    global player_image
    engine.shape_mode = ShapeMode.CENTER
    player_image.draw_fixed_size(player_position_X, player_position_Y, player_size, player_size, False)

def rotate_player():
    """
    rotates the player (rotate), by looking at a vector towards somewhere and returns an angle in degrees
    if the images rotation doesn't work, it is probably HIS FOLD :( !!!

    :return: -
    """
    global player_letter_vector, player_letter_unit_vector, player_letter_vector_length, player_normalized_letter_vector
    global player_dot_vector, player_dot_unit_vector, player_dot_vector_length, player_normalized_dot_vector
    global player_angle, player_angle_rounded, player_angle_converted, player_current_angle
    global player_image

    mouse_x = engine.mouse_x
    mouse_y = engine.mouse_y
    vector_x = mouse_x - player_position_X
    vector_y = mouse_y - player_position_Y

    if len(active_words) > 0: player_letter_vector = (player_position_X, player_position_Y, active_words_positions[target_word][0] - (20 * len(active_words[target_word])), active_words_positions[target_word][1])
    elif len(active_words) < 0: player_letter_vector = (player_position_X, player_position_Y, player_position_X, player_position_Y + 1)
    elif target_word == -1: player_letter_vector = (player_position_X, player_position_Y, player_position_X, player_position_Y + 1)
    player_letter_unit_vector = calc.vector((player_letter_vector[0], player_letter_vector[1]), (player_letter_vector[2], player_letter_vector[3]))
    player_letter_vector_length = calc.vector_length(player_letter_unit_vector)
    player_normalized_letter_vector = calc.normalize_vector(player_letter_unit_vector, player_letter_vector_length)

    # calc player -> dot vector
    player_dot_unit_vector = calc.vector((player_dot_vector[0], player_dot_vector[1]), (player_dot_vector[2], player_dot_vector[3]))
    player_dot_vector_length = calc.vector_length(player_dot_unit_vector)
    player_normalized_dot_vector = calc.normalize_vector(player_dot_unit_vector, player_dot_vector_length)

    # calc player angle in degrees
    player_angle = calc.dot_product(player_dot_unit_vector, player_letter_unit_vector, player_dot_vector_length, player_letter_vector_length)
    player_angle = math.degrees(player_angle)
    # if engine.mouse_y > player_position_y:
    #     angle_difference = 180 - player_angle
    #     player_angle = 180 + angle_difference
    #     if player_angle >= 357.5:
    #         player_angle = 0

    # rotate images
    # player_angle_converted = int((player_angle + 0.5) / 1) #perf
    player_angle_converted = int((player_angle + 2.5) / 1)
    player_angle_rounded = player_angle_converted * 1

    if player_current_angle > player_angle_converted:
        player_current_angle -= 1
    elif player_current_angle < player_angle_converted:
        player_current_angle += 1
    # player_angle_min = player_angle
    print("current angle", player_current_angle)
    print("angle conv", player_angle_converted)

    player_image = player_image_collection[player_current_angle // image_collection_step]

def draw_target():
    """
    draw's a very dark gray line towards a word
    it is verry unnoticeable but adds an extra feature

    :return: -
    """
    engine.outline_color = 0.05, 0.05, 0.05
    engine.draw_line(player_letter_vector[0], player_letter_vector[1], player_letter_vector[2], player_letter_vector[3])

# SCORES

# timers
def update_second_timer():
    """
    counts the seconds, starts counting ofcourse from the moment you start the game
    :return: -
    """
    global play_clock, play_total_time, play_counter_hour, play_counter_min, play_counter_sec, play_counter_sec_fps
    global word_generate_speed, word_fall_speed

    # playtime adds an hour
    if play_counter_min >= 60:
        play_counter_hour += 1
        play_counter_min = 0

        play_total_time[0] += 1 # add hour

        play_clock[0] += 1 # add hour
        play_clock[1] = 0  # rem minutes

    # playtime adds a minute
    if play_counter_sec >= 60:
        play_counter_min += 1
        play_counter_sec = 0

        play_total_time[1] += 1 # add minute

        play_clock[1] += 1 # add minute
        play_clock[2] = 0  # rem seconds

    # playtime adds a second
    if play_counter_sec_fps == play_counter_sec_max:
        play_counter_sec    += 1
        play_counter_sec_fps = 0

        play_total_time[2]  += 1 # add seconds
        play_clock[2]       += 1 # add seconds

        word_generate_speed -= word_speed_increase
        word_fall_speed     += word_speed_increase

        # sets a maximum on how fast a word can fal
        if word_fall_speed > word_fall_speed_max: word_fall_speed = 2

        common.print_info(word_fall_speed)
        common.print_info(word_fall_speed)

    else:
        play_counter_sec_fps += 1

    if     (play_counter_sec == 0 and play_counter_sec_fps == 1 and play_total_time[2] == 0)\
        or (play_counter_sec == 1 and play_counter_sec_fps == 1 and play_total_time[2] == 1)\
        or (play_counter_sec == 2 and play_counter_sec_fps == 1 and play_total_time[2] == 2):
        # play sound on seconds 0, 1, and 2, this works if word generate speed = 3
        sound.play_note("c", 4, 16)
    if     (play_counter_sec == 3 and play_counter_sec_fps == 0 and play_total_time[2] == 3):
        sound.play_note("c", 5, 16)
    if     (play_counter_sec == 0 and play_counter_sec_fps == 0 and play_total_time[2] != 0):
        sound.play_note("c", 5, 16)

# BACKGROUND
def draw_background(color: tuple = (0, 0, 0), alpha: float = 0.2):
    """
    draw's a black 90% transparent rectangle over the background and a solid black rectangle over the player position
    to receive a cool fade effect

    :param color: the color of the background
    :param alpha: the transparency of the background, creates the fading effect

    :return: -
    """
    outline = 0
    colors.color_alpha = (color[0], color[1], color[2], alpha)

    engine.shape_mode = ShapeMode.CORNER

    engine.color = colors.color_alpha
    engine.color = 0, 0, 0, 0.1
    engine.draw_rectangle(0, 0, engine.width, engine.height)
    engine.outline_color = color[0], color[1], color[2]
    engine.draw_rectangle(0, 0, engine.width, engine.height)

    engine.color = colors.color_alpha
    engine.draw_circle(player_position_X - player_size / 2, player_position_Y - player_size / 2, player_size, outline)


# LOADING
def draw_loading(loading_state: int = 0):
    # temp word niet gebruikt denk ik
    """
    draws a big loading screen when starting

    :return: a big loading screen
    """
    engine.shape_mode = ShapeMode.CENTER

    engine.color = colors.blue

    font_size = engine.height // 15

    engine.set_font(fonts.strong_font)
    engine.set_font_size(font_size)

    engine.draw_text("loading ...", center_X, center_Y, True)

def update_loading():
    """
    updates loading bar

    :return: updated loading bar
    """
    global loading_time

    loading_time += 1 / engine.fps
    common.print_info(loading_time)


def draw_start_screen():
    """
    Draws a big play "button" in the center of the screen at the start screen
    It looks like a button, but it doesn't have clickable button functionality

    :return: a fake play button (no button)
    """
    engine.shape_mode = ShapeMode.CENTER

    engine.set_font(fonts.strong_font)

    size = 20

    # click to start background
    engine.color = 0, 0, 0
    engine.draw_rectangle(engine.width / 2, engine.height / 2, engine.width * 0.7, engine.height * 0.1)

    # arrows
    animated_icon_size = icon_size // size * animation_play_size
    icon_right.draw_fixed_size(icon_L_left, icon_L_top, animated_icon_size, animated_icon_size, True)
    icon_left.draw_fixed_size(icon_R_left, icon_R_top, animated_icon_size, animated_icon_size, True)

    # click to start
    engine.set_font_size(large_viewport_edge // 20)

    engine.color = colors.l_orange

    engine.draw_text("click to start", engine.width / 2, engine.height / 2 - large_viewport_edge // 20 * animation_play_size * 0.1, True)

    # title
    engine.set_font_size(int(large_viewport_edge / 15 * animation_play_size))

    engine.color = colors.purple[0], colors.purple[1], colors.purple[2]

    engine.draw_text(f"{game_title}", engine.width / 2, engine.height // 3 - large_viewport_edge // 20 * animation_play_size * 0.1, True)

    # subtitle
    subtitle_animation = 1 - animation_play_size * -150

    engine.set_font(fonts.strong_font)
    engine.set_font_size(int(large_viewport_edge / 40))

    engine.color = colors.green[0], colors.green[1], colors.green[2]

    engine.draw_text(subtitle, engine.width * 0.5 + subtitle_animation, engine.height * 0.4 - large_viewport_edge // 20 * animation_play_size * 0.1, True)

    engine.shape_mode = ShapeMode.CORNER

    engine.set_font(fonts.mono_bold_font)
    engine.set_font_size(16)
    engine.color = 0.5, 0.5, 0.5
    engine.draw_text("by Lennert De Kegel", 20, engine.height - 20 - 16)

def hover_start():
    """
    draws a circle cursor thing on the place of your cursor when hovering over click to start

    :return: - cursor circle
    """

    # if engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, engine.width / 2, engine.height / 2, engine.width * 0.7 - 40, engine.height * 0.1 - 20): #perf
        # draw_cursor() #perf
    pass


# PROJECTILES
# bullets for letter mining animation
def add_bullet(target: tuple = (engine.mouse_x, engine.mouse_y), origin: tuple = (player_position_X, player_position_Y), color: tuple = colors.purple):
    """
    get a new missile ready to shoot

    :param target: direction of the vector
    :param origin: origin of the vector

    :param color: the color of a bullet

    :return: pew pew pew
    """
    global bullet_color, bullet_direction, bullet_unit_vector, bullet_vector_length, bullet_normalized_vector

    # calculate vectors and velocity things
    bullet_unit_vector = calc.vector(origin, target) # get vector
    bullet_unit_vector = calc.mirror_vector(bullet_unit_vector, "X")
    bullet_vector_length = calc.vector_length(bullet_unit_vector) # gets length
    bullet_normalized_vector = calc.normalize_vector(bullet_unit_vector, bullet_vector_length) # normalize the vector

    bullet_converted_velocity.append([bullet_normalized_vector[0] * bullet_speed, bullet_normalized_vector[1] * bullet_speed])                       # add bullet to bullet collection
    bullet_converted_vector.append([origin[0] + bullet_normalized_vector[0] * bullet_speed, origin[1] + bullet_normalized_vector[1] * bullet_speed]) # add bullet COORDINATES to bullet collection

    color = color[0], color[1], color[2]

    bullet_color.append(color)

def draw_bullet():
    """
    draws bullet

    :return: -
    """
    engine.shape_mode = ShapeMode.CENTER

    for index in range(len(bullet_converted_vector)):
        engine.outline_color = None
        common.print_info(bullet_converted_vector)

        if len(bullet_converted_vector) <= 0: break
        if len(bullet_color) >= 0: bullet_color[index]

        # outer layer
        if bullet_color[index] == colors.l_green:  bullet_color[index] = colors.green
        if bullet_color[index] == colors.l_blue:   bullet_color[index] = colors.blue
        if bullet_color[index] == colors.l_orange: bullet_color[index] = colors.orange
        if bullet_color[index] == colors.l_red:    bullet_color[index] = colors.red
        if bullet_color[index] == colors.l_purple: bullet_color[index] = colors.purple

        # randomize for outer layer
        add_random_X = random.uniform(-1, 1)
        add_random_Y = random.uniform(-1, 1)

        engine.color = bullet_color[index]

        engine.draw_circle(bullet_converted_vector[index][0] + add_random_X, bullet_converted_vector[index][1] + add_random_Y, projectile_size, 0)

        # inner layer
        if bullet_color[index] == colors.green:  bullet_color[index] = colors.l_green
        if bullet_color[index] == colors.blue:   bullet_color[index] = colors.l_blue
        if bullet_color[index] == colors.orange: bullet_color[index] = colors.l_orange
        if bullet_color[index] == colors.red:    bullet_color[index] = colors.l_red
        if bullet_color[index] == colors.purple: bullet_color[index] = colors.l_purple

        # randomize for inner layer
        add_random_X = random.uniform(-2, 2)
        add_random_Y = random.uniform(-2, 2)

        engine.color = bullet_color[index]
        engine.draw_circle(bullet_converted_vector[index][0] + add_random_X, bullet_converted_vector[index][1] + add_random_Y - 1, projectile_size * 0.8, 0)

def update_bullet():
    """
    updates missiles, makes them move around and stuff
    :return: -
    """
    global bullet_converted_vector

    for index in range(len(bullet_converted_vector)):
        if len(bullet_converted_vector) == 0: break
        bullet_converted_vector[index][0] += bullet_converted_velocity[index][0]
        bullet_converted_vector[index][1] += bullet_converted_velocity[index][1]

def check_bullet():
    """
    checks if a missile is within viewport boundaries
    :return: -
    """
    global bullet_converted_velocity, bullet_converted_vector

    for index in range(len(bullet_converted_vector)):
        if len(bullet_converted_vector) == 0: break

        if bullet_converted_vector[index][0] <= 0 \
                or bullet_converted_vector[index][0] >= engine.width \
                or bullet_converted_vector[index][1] <= 0 \
                or bullet_converted_vector[index][1] >= engine.height:
            bullet_converted_vector.pop(index)
            bullet_converted_velocity.pop(index)

            bullet_color.pop(index)
            break

        if bullet_converted_vector[index][1] > player_position_Y:
            bullet_converted_vector.pop(index)
            bullet_converted_velocity.pop(index)

            bullet_color.pop(index)
            break

        bullet_converted_vector[index][0] += bullet_converted_velocity[index][0]
        bullet_converted_vector[index][1] += bullet_converted_velocity[index][1]

def add_flare(target: tuple = (player_position_X, player_position_Y), color: tuple = colors.orange):
    """
    get a new flare ready to lose

    :param target: direction of the vector
    :param color:  the color of a flare

    :return: a flare to collections
    """
    global flare_direction, flare_unit_vector, flare_vector_length, flare_normalized_vector, flare_speed, flare_converted_velocity, flare_converted_vector, flare_color, flare_points_collection

    full_angles_per_second = 1
    angle_per_time_increment = (play_counter_sec_fps / 60) * (2 * math.pi) * full_angles_per_second
    flare_point = calc.unit_circle((player_position_X, player_position_Y), player_size / 2, angle_per_time_increment, "rad")

    flare_unit_vector = calc.vector(flare_point, target)

    flare_unit_vector = calc.mirror_vector(flare_unit_vector, "Y") # mirroring over Y axes, for engine to work
    flare_unit_vector = calc.flip_vector(flare_unit_vector) # flips the vector completely

    flare_unit_vector = calc.flip_vector(flare_unit_vector)
    flare_vector_length = calc.vector_length(flare_unit_vector)
    flare_normalized_vector = calc.normalize_vector(flare_unit_vector, flare_vector_length)

    # adds flare velocity and vector to collection
    # flare_point.append(flare_point)
    flare_points_collection.append(flare_point)

    flare_converted_vector.append([flare_point[0], flare_point[1]])  # add flare COORDINATES to flare collection
    flare_converted_velocity.append([flare_normalized_vector[0] * flare_speed, flare_normalized_vector[1] * flare_speed])  # add flare to flare collection

    flare_color.append(colors.red)
    flare_timer.append(flare_duration)

def draw_flare():
    """
    draws flares

    :return: -
    """
    engine.shape_mode = ShapeMode.CENTER

    for index in range(len(flare_converted_vector)):
        engine.outline_color = None

        if len(flare_converted_vector) <= 0: break
        if len(flare_color) <= 0: engine.color = colors.red

        # outer layer
        if flare_color[index] == colors.l_green:  flare_color[index] = colors.green
        if flare_color[index] == colors.l_blue:   flare_color[index] = colors.blue
        if flare_color[index] == colors.l_orange: flare_color[index] = colors.orange
        if flare_color[index] == colors.l_red:    flare_color[index] = colors.red
        if flare_color[index] == colors.l_purple: flare_color[index] = colors.purple

        engine.color = flare_color[index]
        # randomize for outer layer
        add_random_X = random.uniform(-1, 1)
        add_random_Y = random.uniform(-1, 1)

        engine.draw_circle(flare_converted_vector[index][0] + add_random_X, flare_converted_vector[index][1] + add_random_Y, projectile_size, 0)

        # inner layer
        if flare_color[index] == colors.green:  flare_color[index] = colors.l_green
        if flare_color[index] == colors.blue:   flare_color[index] = colors.l_blue
        if flare_color[index] == colors.orange: flare_color[index] = colors.l_orange
        if flare_color[index] == colors.red:    flare_color[index] = colors.l_red
        if flare_color[index] == colors.purple: flare_color[index] = colors.l_purple

        engine.color = flare_color[index]

        # randomize for inner layer
        add_random_X = random.uniform(-2, 2)
        add_random_Y = random.uniform(-2, 2)
        engine.draw_circle(flare_converted_vector[index][0] + add_random_X, flare_converted_vector[index][1] + add_random_Y, projectile_size * 0.8, 0)

        print("flare timer: ", flare_timer[index])

def update_flare():
    """
    updates the position and velocity

    applying the velocity to the position, so it will move

    :return: -
    """
    global flare_converted_vector, flare_timer

    for index in range(len(flare_converted_vector)):
        add_random_X = random.uniform(-3, 3)
        add_random_Y = random.uniform(-3, 3)

        if len(flare_converted_vector) == 0: break
        flare_converted_vector[index][0] += add_random_Y
        flare_converted_vector[index][1] += add_random_Y

        flare_converted_vector[index][0] += flare_converted_velocity[index][0]
        flare_converted_vector[index][1] += flare_converted_velocity[index][1]

        flare_timer[index] -= 1

def check_flare():
    """
    checks if flares are visible,

    deletes values to flare globals, to delete the flare)
    deleting is needed for memory space)

    :return: -
    """
    global flare_converted_velocity, flare_converted_vector, flare_color, flare_timer

    for index in range(len(flare_converted_vector)):
        if len(flare_converted_vector) == 0: break

        if flare_timer[index] <= 0:
            flare_converted_vector.pop(index)
            flare_converted_velocity.pop(index)

            flare_color.pop(index)
            flare_timer.pop(index)
            break

        engine.shape_mode = ShapeMode.CORNER

        if flare_converted_vector[index][0] <= 0 \
                or flare_converted_vector[index][0] >= engine.width \
                or flare_converted_vector[index][1] <= 0 \
                or flare_converted_vector[index][1] >= engine.height:
            flare_converted_vector.pop(index)
            flare_converted_velocity.pop(index)

            flare_color.pop(index)
            flare_timer.pop(index)
            break

        flare_converted_vector[index][0] += flare_converted_velocity[index][0]
        flare_converted_vector[index][1] += flare_converted_velocity[index][1]

def draw_laser_beam(target: tuple, origin: tuple = (player_position_X, player_position_Y), size: int = projectile_size, color: tuple = colors.red):
    """
    recommended to use this function only for an instant, not al the time

    :param target: the target to where the beam will go
    :param origin: the origin of where the beam starts form

    :param size: the size of the beam, is relative
    :param color: the color of the beam

    :return: a big powerful laser beam, pew
    """
    color                = color[0], color[1], color[2]
    engine.outline_color = color[0], color[1], color[2]

    add_left   = -1 * projectile_size // 5
    add_right  = 1 * projectile_size // 5
    add_bottom = projectile_size // 2
    engine.draw_line(origin[0] + add_left * add_bottom, origin[1], target[0], target[1], size * 2)
    engine.draw_line(origin[0] + add_right * add_bottom, origin[1], target[0], target[1], size * 2)

    # inner layer
    if color == colors.green:     color = colors.l_green
    if color == colors.blue:      color = colors.l_blue
    if color == colors.orange:    color = colors.l_orange
    if color == colors.red:       color = colors.l_red
    if color == colors.purple:    color = colors.l_purple

    if color == colors.l_purple2: color = colors.l_purple1
    if color == colors.d_purple2: color = colors.d_purple1

    color                = color[0], color[1], color[2]
    engine.outline_color = color[0], color[1], color[2]

    # inner layer
    engine.draw_line(origin[0], origin[1], target[0], target[1] - 5, size // 2)


# WORDS
def setup_words():
    """
    assigns words of difficulty collections to the main word collection
    it is based on the difficulty, if the player selected for example the highers difficulty,
    this will make the main word collection include every word collection lower and equal to the selected difficulty

    :return: The complete main word collection
    """
    global main_word_collection, active_words, active_words_positions

    active_words.append(random.choice(tuple(main_word_collection)))
    active_words_positions.append([random.uniform(20, engine.width - 20 - 20 * len(active_words[-1]) - 1), 0 - fonts.normal_text_size])

def get_words():
    """
    generates a random word on a time based period.

    :return: -
    """
    global play_word_counter, active_words, active_words_positions

    save_word_counter = play_word_counter
    play_word_counter = int(play_counter_sec * 1 // word_generate_speed)
    if save_word_counter != play_word_counter:
        # for word in range(len(current_words)): # CHECKPOINT: als tijd over
        if not len(active_words) >= max_words:
            get_word = random.choice(list(main_word_collection))
            active_words.append(get_word)
            active_words_positions.append([random.uniform(20 + len(get_word) * 20, engine.width), 0 - fonts.normal_text_size])
            sound.play_note("re+", 7, 128)

def draw_words():
    """
    this will draw the words on the screen

    :return: some words will be shown on the screen
    """
    global score_right_words

    for word_index in range(len(active_words)):
        if len(active_words) == 0: break

        engine.set_font(fonts.strong_font)
        engine.set_font_size(fonts.heading_text_size)

        letter_spacing = 20
        letter_position_X = len(active_words[word_index]) * -20

        for letter in range(len(active_words[word_index])):
            current_word = list(active_words[word_index])

            engine.shape_mode = ShapeMode.CENTER

            engine.color = 0, 0, 0
            engine.outline_color = None

            if word_index == target_word:
                engine.color = 0, 0, 0
                engine.outline_color = colors.orange[0], colors.orange[1], colors.orange[2]

                engine.draw_rectangle(active_words_positions[word_index][0] + letter_position_X, active_words_positions[word_index][1], 20, 20)

            engine.outline_color = None
            engine.draw_rectangle(active_words_positions[word_index][0] + letter_position_X, active_words_positions[word_index][1] - 1, 22, 19)

            engine.color = 1, 1, 1

            engine.draw_text(f"{current_word[letter]}", active_words_positions[word_index][0] + letter_position_X, active_words_positions[word_index][1] - 2, True)

            letter_position_X += letter_spacing

def update_words():
    """
    Moves the words towards the player on the y-axis and handles word removal.
    """
    global active_words, active_words_positions, score_wrong_words, score_right_words, target_word

    for word in range(len(active_words) - 1, -1, -1):
        # start (index), stop (moet -1 zijn om enkel uit te voeren als list leeg is), step (-1, for inverting looping over range)
        # controlleer

        # Checks if word is empty and deletes it if that is true
        if len(active_words[word]) == 0:
            # un target the word that gets deleted
            target_word = -1

            # deletes the words with its position out of the collection
            active_words.pop(word)
            active_words_positions.pop(word)

            # score updating
            score_right_words += 1

            # beep
            sound.play_note("re", 5, 128)
            continue

        # Update position of all words
        active_words_positions[word][1] += word_fall_speed

        # word will get deleted, if it will touch the player (dead zone)
        if active_words_positions[word][1] >= player_position_Y - player_size / 2 - 20:
            # deletes the word from the collection with its position
            active_words.pop(word)
            active_words_positions.pop(word)

            if target_word != -1 and word == 0: target_word = -1

            # updates score.
            score_wrong_words += 1

            sound.play_note("sol", 2, 8)
            sound.play_note("sol", 1, 8)

def check_words():
    """
    checks letters, and locks words

    :return: -
    """
    global score_right_words, score_right_letters, score_wrong_words, score_wrong_letters, save_score_wrong_letter
    global target_word, target_key, save_key

    # if NO WORD is TARGETED yet, it will look at every single word
    if target_word == -1:
        # loops over every word in the active word collection
        for word in range(len(active_words) - 1, -1, -1):
            # if current_words collection is empty, break the loop and no errors will appear
            if len(active_words) == 0: break

            # loops over every letter of the current looped over word
            for letter in range(len(active_words[word])):

                # CHECKPOINT (deze code kan geen nut hebben, verwijder eens na aanpassingen)
                # if len(active_words[word]) == 0: break

                if target_key == active_words[word][0] and save_key != target_key:
                    # lock word if letter is in word
                    target_word = word

    # if A WORD is TARGETED, it will look at only that specific targeted word
    if target_word >= 0:
        # CHECKPOINT (delete if not needed)
        if target_word > len(active_words) - 1:
            common.print_error("target_word (index) out of (index range) active_words (collection): ", f"target_word: {target_word} ", f"len(active_words): {len(active_words)} ", "idk")
            target_word = -1
            pass

        # assigns the word to target
        word_index = target_word

        # loops over every letter of the current word (targeted word)
        for letter in range(len(active_words[word_index])):

            if save_key != target_key:
                # checks if user input is same as letter input
                if target_key == active_words[word_index][0]:
                    # pops the first letter out of the current word
                    active_words[word_index] = active_words[word_index][1:]

                    # LSW save_score_wrong_letter = score_wrong_letters

                    # update score
                    score_right_letters += 1
                    score_wrong_letters -= 1 # work around

                    origin_X = active_words_positions[word_index][0] - (20 * len(active_words[word_index])) - 20
                    origin_Y = active_words_positions[word_index][1] + 15

                    # add a bullet that by magic will move for esthetics
                    add_bullet((player_position_X, player_position_Y), (origin_X, origin_Y), colors.green)

                    # draws a beam, that will fade away fast, due tu the partially transparent background
                    draw_laser_beam(target = (origin_X, origin_Y), color = colors.d_purple2, size = 1)

                # if not it will change a player negative score
                elif target_key != active_words[word_index][0]:
                    common.print_info("boba")
                    break

            save_key = target_key

    if save_score_wrong_letter != score_wrong_letters:
        add_flare()
        save_score_wrong_letter = score_wrong_letters

# BACKGROUND
def setup_position_stars():
    """
    gives random position to stars only at the start of the program
    :return: -
    """
    global star_positions

    # hier for lus, zelfde als in draw_stars()
    for counter in range(stars_amount):
        stars_xPositions_list.append(random.randint(0, engine.width))
        stars_yPositions_list.append(random.randint(0, engine.height))

def draw_stars():
    """
    draws a star at the end of the
    :param pos_x: center x of circle
    :param pos_y: center y of circle
    :return: -
    """
    global star_positions

    engine.shape_mode = ShapeMode.CENTER

    engine.outline_color = None
    engine.color = 1, 1, 1, 0.8

    for counter in range(stars_amount):
        engine.draw_circle(stars_xPositions_list[counter], stars_yPositions_list[counter], star_size, 0)

def update_stars():
    """
    moves star to the left

    :return: updates the position of the stars
    """
    global player_mouse_vector, player_mouse_unit_vector, player_mouse_vector_length, player_normalized_mouse_vector
    global star_positions, stars_direction, stars_speed
    stars_direction = player_normalized_mouse_vector[0] * -1, player_normalized_mouse_vector[1]

    # calc player -> letter vector, for rotating stars around
    player_mouse_vector = (player_position_X, player_position_Y, engine.mouse_x, engine.mouse_y)
    player_mouse_unit_vector = calc.vector((player_mouse_vector[0], player_mouse_vector[1]), (player_mouse_vector[2], player_mouse_vector[3]))
    player_mouse_vector_length = calc.vector_length(player_mouse_unit_vector)
    player_normalized_mouse_vector = calc.normalize_vector(player_mouse_unit_vector, player_mouse_vector_length)

    # for lus maken
    for counter in range(stars_amount):
        stars_xPositions_list[counter] += stars_direction[0] * stars_speed
        stars_yPositions_list[counter] += stars_direction[1] * stars_speed

        # right
        # 0deg
        if stars_xPositions_list[counter] >= engine.width + star_size / 2:
            stars_xPositions_list[counter] -= engine.width - star_size / 2

        # top
        # 90deg
        if stars_yPositions_list[counter] <= 0 - star_size / 2:
            stars_yPositions_list[counter] += engine.height + star_size / 2

        # left
        # 180deg
        if stars_xPositions_list[counter] <= 0 - star_size / 2:
            stars_xPositions_list[counter] = engine.width + star_size / 2

        # bottom
        # 270deg
        if stars_yPositions_list[counter] >= engine.height + star_size:
            stars_yPositions_list[counter] = 0 - star_size / 2

# MENU
def draw_menu(color_top: str, color_side: str, menu_title: str, menu_subtitle: str, L_text: tuple, R_text: tuple, L_color: tuple, R_color: tuple):
    """
    draw's a menu that with specific colors per menu

    :param color_top:     top color accent
    :param color_side:    side color accent
    standard NORMAL
    options menu colors for both top and side are: LIGHT, NEUTRAL, NORMAL, DARK

    :param menu_title:         title of the menu
    :param menu_subtitle:      subtitle, optional

    :param L_text:   the text written on the left half
    standard STRONG
    :param R_text:  the text written on the right half
    standard MONO

    :param L_color:  the text colors per row on the left half
    :param R_color: the text colors per row on the right half
    standard WHITE

    :return: a beautiful menu
    """
    global menu_outer_animation_scale, menu_outer_animation_direction, \
           menu_top_animation_scale, menu_top_animation_direction

    # for drawing text
    row_amount          = 9
    text_white_spacing  = 0.6
    ruler_start         = small_viewport_edge / 4
    ruler_spacing       = large_viewport_edge / 40.5
    whitespace          = large_viewport_edge / 300

    menu_title_ruler    = (engine.height / 4.5 - 30 * whitespace) * viewport_scaler
    menu_subtitle_ruler = (engine.height / 4.5) * viewport_scaler

    text_ruler_1 = (ruler_start + 0 * ruler_spacing + 1 * whitespace) * viewport_scaler
    text_ruler_2 = (ruler_start + 1 * ruler_spacing + 1 * whitespace) * viewport_scaler
    text_ruler_3 = (ruler_start + 2 * ruler_spacing + 1 * whitespace) * viewport_scaler
    text_ruler_4 = (ruler_start + 3 * ruler_spacing + 1 * whitespace) * viewport_scaler
    text_ruler_5 = (ruler_start + 4 * ruler_spacing + 1 * whitespace) * viewport_scaler
    text_ruler_6 = (ruler_start + 5 * ruler_spacing + 1 * whitespace) * viewport_scaler
    text_ruler_7 = (ruler_start + 6 * ruler_spacing + 1 * whitespace) * viewport_scaler
    text_ruler_8 = (ruler_start + 7 * ruler_spacing + 2 * whitespace) * viewport_scaler
    text_ruler_9 = (ruler_start + 8 * ruler_spacing + 2 * whitespace) * viewport_scaler
    # extra
    safety_break = False

    # FUNCTIONS - causes somewhat big fps drops
    menu_outer_animation_scale, menu_outer_animation_direction = scale_animation(menu_outer_animation_scale, menu_outer_animation_direction, 0.015)
    menu_top_animation_scale, menu_top_animation_direction = scale_animation(menu_top_animation_scale, menu_top_animation_direction, 0.1)

    # RESET
    engine.color = colors.white
    engine.outline_color = None

    # [images]
    engine.shape_mode = ShapeMode.CENTER

    # DRAW MENU'S BACKGROUND

    # side
    # » layer 1
    if color_side.lower() == "light":     menu_side_light_image.draw_fixed_size(center_X, center_Y, menu_size, menu_size, True)
    elif color_side.lower() == "neutral": menu_side_neutral_image.draw_fixed_size(center_X, center_Y, menu_size, menu_size, True)
    elif color_side.lower() == "normal":  menu_side_normal_image.draw_fixed_size(center_X, center_Y, menu_size, menu_size, True)
    elif color_side.lower() == "dark":    menu_side_dark_image.draw_fixed_size(center_X, center_Y, menu_size, menu_size, True)
    else:                                 menu_top_normal_image.draw_fixed_size(center_X, center_Y, menu_size, menu_size, True)

    # outer
    # » layer 2
    menu_outer_image.draw_fixed_size(center_X, center_Y, menu_size * menu_outer_animation_scale, menu_size * menu_outer_animation_scale, True)

    # top
    # » layer 3
    if color_top.lower() == "light":      menu_top_light_image.draw_fixed_size(center_X, center_Y, menu_size * menu_top_animation_scale, menu_size, False)
    elif color_top.lower() == "neutral":  menu_top_neutral_image.draw_fixed_size(center_X, center_Y, menu_size * menu_top_animation_scale, menu_size, False)
    elif color_top.lower() == "normal":   menu_top_normal_image.draw_fixed_size(center_X, center_Y, menu_size * menu_top_animation_scale, menu_size, False)
    elif color_top.lower() == "dark":     menu_top_dark_image.draw_fixed_size(center_X, center_Y, menu_size * menu_top_animation_scale, menu_size, False)
    else:                                 menu_top_normal_image.draw_fixed_size(center_X, center_Y, menu_size * menu_top_animation_scale, menu_size, False)

    # MAIN
    menu_main_image.draw_fixed_size(center_X, center_Y, menu_size, menu_size, True)


    # VALUE CONTROL

    # » checking TEXT tuples
    # reforms column tuples to lists, to append values if needed
    L_text  = list(L_text)
    R_text = list(R_text)

    # checks if there are 7 columns if not it will full it up to 7
    while len(L_text) != row_amount:
        L_text.append("")

    while len(R_text) != row_amount:
        R_text.append("")

    # reforms column list back to tuples after the possible changes have been made
    L_text  = tuple(L_text)
    R_text = tuple(R_text)

    # » checking COLOR tuples
    # reforms column tuples to lists, to append values if needed
    L_color = list(L_color)
    R_color = list(R_color)

    # checks if there are 7 columns if not it will full it up to 7
    # left column
    for index in range(len(L_color)):
        if safety_break: break
        if type(L_color[index]) != tuple:
            common.print_error("type", f"left_color_column[{index}] ", " is no tuple", "invalid value")
            safety_break = True

    while len(L_color) != row_amount:
        if safety_break: break
        L_color.append((1, 1, 1))

    # right column
    for index in range(len(R_color)):
        if safety_break: break
        if type(R_color[index]) != tuple:
            common.print_error("type", f"left_color_column[{index}] ", " is no tuple", "invalid value")
            safety_break = True

    while len(R_color) != row_amount:
        if safety_break: break
        R_color.append((1, 1, 1))

    # reforms column list back to tuples after the possible changes have been made
    L_color = tuple(L_color)
    R_color = tuple(R_color)


    # [text]
    engine.set_font(fonts.strong_font)
    engine.set_font_size(fonts.heading_text_size)

    engine.draw_text(str(menu_title), center_X, menu_title_ruler, True) # menu title
    engine.draw_text(str(menu_subtitle), justify_text_left, menu_subtitle_ruler, False) # subtitle

    # » COLUMNS
    # left column
    engine.set_font(fonts.normal_font)
    engine.set_font_size(fonts.heading_text_size)

    index = 0
    engine.color = L_color[index]
    engine.draw_text(str(L_text[index]), justify_text_left, text_ruler_1, False)

    index = 1
    engine.color = L_color[index]
    engine.draw_text(str(L_text[index]), justify_text_left, text_ruler_2, False)

    index = 2
    engine.color = L_color[index]
    engine.draw_text(str(L_text[index]), justify_text_left, text_ruler_3, False)

    index = 3
    engine.color = L_color[index]
    engine.draw_text(str(L_text[index]), justify_text_left, text_ruler_4, False)

    index = 4
    engine.color = L_color[index]
    engine.draw_text(str(L_text[index]), justify_text_left, text_ruler_5, False)

    index = 5
    engine.color = L_color[index]
    engine.draw_text(str(L_text[index]), justify_text_left, text_ruler_6, False)

    index = 6
    engine.color = L_color[index]
    engine.draw_text(str(L_text[index]), justify_text_left, text_ruler_7, False)

    index = 7
    engine.color = L_color[index]
    engine.draw_text(str(L_text[index]), justify_text_left, text_ruler_8, False)

    engine.set_font(fonts.strong_font)
    engine.set_font_size(fonts.heading_text_size)

    index = 8
    engine.color = L_color[index]
    engine.draw_text(str(L_text[index]), justify_text_left, text_ruler_9, False)


    # right column
    engine.set_font(fonts.mono_font)
    engine.set_font_size(fonts.heading_text_size)
    font_size = fonts.heading_text_size

    index = 0
    engine.color = R_color[index]
    engine.draw_text(str(R_text[index]), justify_text_right - len(str(R_text[index])) * text_white_spacing * font_size, text_ruler_1, False)

    index = 1
    engine.color = R_color[index]
    engine.draw_text(str(R_text[index]), justify_text_right - len(str(R_text[index])) * text_white_spacing * font_size, text_ruler_2, False)

    index = 2
    engine.color = R_color[index]
    engine.draw_text(str(R_text[index]), justify_text_right - len(str(R_text[index])) * text_white_spacing * font_size, text_ruler_3, False)

    index = 3
    engine.color = R_color[index]
    engine.draw_text(str(R_text[index]), justify_text_right - len(str(R_text[index])) * text_white_spacing * font_size, text_ruler_4, False)

    index = 4
    engine.color = R_color[index]
    engine.draw_text(str(R_text[index]), justify_text_right - len(str(R_text[index])) * text_white_spacing * font_size, text_ruler_5, False)

    index = 5
    engine.color = R_color[index]
    engine.draw_text(str(R_text[index]), justify_text_right - len(str(R_text[index])) * text_white_spacing * font_size, text_ruler_6, False)

    index = 6
    engine.color = R_color[index]
    engine.draw_text(str(R_text[index]), justify_text_right - len(str(R_text[index])) * text_white_spacing * font_size, text_ruler_7, False)

    index = 7
    engine.color = R_color[index]
    engine.draw_text(str(R_text[index]), justify_text_right - len(str(R_text[index])) * text_white_spacing * font_size, text_ruler_8, False)

    engine.set_font_size(fonts.heading_text_size)

    index = 8
    engine.color = R_color[index]
    engine.draw_text(str(R_text[index]), justify_text_right - len(str(R_text[index])) * text_white_spacing * font_size, text_ruler_9, False)

# BUTTONS
def draw_M_button(grid_position: int = 0, color: str = "standard", text: str = "", animation: bool = False):
    """
    draws a medium size button with text at place on grid

    :param grid_position: An integer of where the button has to be positioned
    standard = 0 (=> don't draw)
                    1 | 2
    grid positions: --+--
                    3 | 4

    :param color: the color of the button, string
    standard = gray

    :param text: the text on the button

    :param animation: condition to animation scale
    standard = False

    :return: a medium button in the grid
    """
    engine.shape_mode = ShapeMode.CENTER

    engine.set_font(fonts.strong_font)
    engine.set_font_size(30)

    if grid_position == 1 and not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_left, button_up, medium_button_width, button_height):
        if color == "":       button_medium.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)
        if color == "green":  button_medium_green.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)
        if color == "blue":   button_medium_blue.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)
        if color == "orange": button_medium_orange.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)
        if color == "red":    button_medium_red.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)
        if color == "purple": button_medium_purple.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)

        if color != "green": engine.color = colors.gray[0], colors.gray[1], colors.gray[2]
        if color == "green": engine.color = colors.l_purple2[0], colors.l_purple2[1], colors.l_purple2[2]
        engine.draw_text(str(text).upper(), justify_button_left, button_up, True)

    elif grid_position == 1 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_left, button_up, medium_button_width, button_height):
        if color == "":       button_medium_hover.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)
        if color == "green":  button_medium_green_hover.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)
        if color == "blue":   button_medium_blue_hover.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)
        if color == "orange": button_medium_orange_hover.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)
        if color == "red":    button_medium_red_hover.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)
        if color == "purple": button_medium_purple_hover.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)

        engine.draw_text(str(text).upper(), justify_button_left, button_up, True)
        # draw_cursor() #perf


    if grid_position == 2 and not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_right, button_up, medium_button_width, button_height):
        if color == "":       button_medium.draw_fixed_size(justify_button_right, button_up, medium_button_width, button_height, True)
        if color == "green":  button_medium_green.draw_fixed_size(justify_button_right, button_up, medium_button_width, button_height, True)
        if color == "blue":   button_medium_blue.draw_fixed_size(justify_button_right, button_up, medium_button_width, button_height, True)
        if color == "orange": button_medium_orange.draw_fixed_size(justify_button_right, button_up, medium_button_width, button_height, True)
        if color == "red":    button_medium_red.draw_fixed_size(justify_button_right, button_up, medium_button_width, button_height, True)
        if color == "purple": button_medium_purple.draw_fixed_size(justify_button_right, button_up, medium_button_width, button_height, True)

        if color != "green": engine.color = colors.gray[0], colors.gray[1], colors.gray[2]
        if color == "green": engine.color = colors.l_purple2[0], colors.l_purple2[1], colors.l_purple2[2]
        engine.draw_text(str(text).upper(), justify_button_right, button_up, True)

    elif grid_position == 2 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_right, button_up, medium_button_width, button_height):
        if color == "":       button_medium_hover.draw_fixed_size(justify_button_right, button_up, medium_button_width, button_height, True)
        if color == "green":  button_medium_green_hover.draw_fixed_size(justify_button_right, button_up, medium_button_width, button_height, True)
        if color == "blue":   button_medium_blue_hover.draw_fixed_size(justify_button_right, button_up, medium_button_width, button_height, True)
        if color == "orange": button_medium_orange_hover.draw_fixed_size(justify_button_right, button_up, medium_button_width, button_height, True)
        if color == "red":    button_medium_red_hover.draw_fixed_size(justify_button_right, button_up, medium_button_width, button_height, True)
        if color == "purple": button_medium_purple_hover.draw_fixed_size(justify_button_right, button_up, medium_button_width, button_height, True)

        engine.draw_text(str(text).upper(), justify_button_right, button_up, True)
        # draw_cursor() #perf


    if grid_position == 3 and not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_left, button_down, medium_button_width, button_height):
        if color == "":       button_medium.draw_fixed_size(justify_button_left, button_down, medium_button_width, button_height, True)
        if color == "green":  button_medium_green.draw_fixed_size(justify_button_left, button_down, medium_button_width, button_height, True)
        if color == "blue":   button_medium_blue.draw_fixed_size(justify_button_left, button_down, medium_button_width, button_height, True)
        if color == "orange": button_medium_orange.draw_fixed_size(justify_button_left, button_down, medium_button_width, button_height, True)
        if color == "red":    button_medium_red.draw_fixed_size(justify_button_left, button_down, medium_button_width, button_height, True)
        if color == "purple": button_medium_purple.draw_fixed_size(justify_button_left, button_down, medium_button_width, button_height, True)

        if color != "green": engine.color = colors.gray[0], colors.gray[1], colors.gray[2]
        if color == "green": engine.color = colors.l_purple2[0], colors.l_purple2[1], colors.l_purple2[2]
        engine.draw_text(str(text).upper(), justify_button_left, button_down, True)

    elif grid_position == 3 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_left, button_down, medium_button_width, button_height):
        if color == "":       button_medium_hover.draw_fixed_size(justify_button_left, button_down, medium_button_width, button_height, True)
        if color == "green":  button_medium_green_hover.draw_fixed_size(justify_button_left, button_down, medium_button_width, button_height, True)
        if color == "blue":   button_medium_blue_hover.draw_fixed_size(justify_button_left, button_down, medium_button_width, button_height, True)
        if color == "orange": button_medium_orange_hover.draw_fixed_size(justify_button_left, button_down, medium_button_width, button_height, True)
        if color == "red":    button_medium_red_hover.draw_fixed_size(justify_button_left, button_down, medium_button_width, button_height, True)
        if color == "purple": button_medium_purple_hover.draw_fixed_size(justify_button_left, button_down, medium_button_width, button_height, True)

        engine.draw_text(str(text).upper(), justify_button_left, button_down, True)
        # draw_cursor() #perf


    if grid_position == 4 and not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_right, button_down, medium_button_width, button_height):
        if color == "":  button_medium.draw_fixed_size(justify_button_right, button_down, medium_button_width, button_height, True)
        if color == "green":  button_medium_green.draw_fixed_size(justify_button_right, button_down, medium_button_width, button_height, True)
        if color == "blue":   button_medium_blue.draw_fixed_size(justify_button_right, button_down, medium_button_width, button_height, True)
        if color == "orange": button_medium_orange.draw_fixed_size(justify_button_right, button_down, medium_button_width, button_height, True)
        if color == "red":    button_medium_red.draw_fixed_size(justify_button_right, button_down, medium_button_width, button_height, True)
        if color == "purple": button_medium_purple.draw_fixed_size(justify_button_right, button_down, medium_button_width, button_height, True)

        if color != "green": engine.color = colors.gray[0], colors.gray[1], colors.gray[2]
        if color == "green": engine.color = colors.l_purple2[0], colors.l_purple2[1], colors.l_purple2[2]
        engine.draw_text(str(text).upper(), justify_button_right, button_down, True)

    elif grid_position == 4 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_right, button_down, medium_button_width, button_height):
        if color == "":       button_medium_hover.draw_fixed_size(justify_button_right, button_down, medium_button_width, button_height, True)
        if color == "green":  button_medium_green_hover.draw_fixed_size(justify_button_right, button_down, medium_button_width, button_height, True)
        if color == "blue":   button_medium_blue_hover.draw_fixed_size(justify_button_right, button_down, medium_button_width, button_height, True)
        if color == "orange": button_medium_orange_hover.draw_fixed_size(justify_button_right, button_down, medium_button_width, button_height, True)
        if color == "red":    button_medium_red_hover.draw_fixed_size(justify_button_right, button_down, medium_button_width, button_height, True)
        if color == "purple": button_medium_purple_hover.draw_fixed_size(justify_button_right, button_down, medium_button_width, button_height, True)

        engine.draw_text(str(text).upper(), justify_button_right, button_down, True)
        # draw_cursor() #perf

def draw_S_button(position: tuple = 0, color: str = "standard", text: str = "", icon: str = "", animation: bool = False):
    """
    draws a small size button with text or an icon somewhere, you want

    :param position: A tuple with floats acts as coordinates for the buttons position
    standard = 0 (=> don't draw)

    :param color: the color of the button, string
    standard = gray

    :param text: the text on the button
    :param icon: the icon on the button # temp delete if no time left

    :param animation: condition to animation scale
    standard = False

    :return: a small button
    """
    engine.shape_mode = ShapeMode.CENTER

    engine.set_font(fonts.strong_font)
    engine.set_font_size(30)

    if not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, position[0], position[1], small_button_width, button_height):
        if color == "":  button_medium.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)
        if color == "green":  button_medium_green.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)
        if color == "blue":   button_medium_blue.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)
        if color == "orange": button_medium_orange.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)
        if color == "red":    button_medium_red.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)
        if color == "purple": button_medium_purple.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)
        engine.color = colors.gray[0], colors.gray[1], colors.gray[2]
        engine.draw_text(str(text).upper(), justify_button_left, button_up, True)
    elif engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, position[0], position[1], small_button_width, button_height):
        if color == "":  button_medium_hover.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)
        if color == "green":  button_medium_green_hover.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)
        if color == "blue":   button_medium_blue_hover.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)
        if color == "orange": button_medium_orange_hover.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)
        if color == "red":    button_medium_red_hover.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)
        if color == "purple": button_medium_purple_hover.draw_fixed_size(justify_button_left, button_up, medium_button_width, button_height, True)
        engine.color = colors.l_purple1[0], colors.l_purple1[1], colors.l_purple1[2]
        engine.draw_text(str(text).upper(), justify_button_left, button_up, True)
        # draw_cursor() #perf

# custom buttons
def draw_difficulty_button():
    """
    draws the difficulty button

                    1 & 2
    grid positions: --+--
                    × | ×

    :return: the difficulty button
    """
    # GLOBALS
    global difficulty_Y, difficulty_height, hover_difficulty_button

    engine.shape_mode = ShapeMode.CENTER

    engine.set_font(fonts.strong_font)
    engine.set_font_size(30)

    # LOCALS

    if difficulty == "easy":
        # if ACTIVE
        button_card_easy.draw_fixed_size(center_X - partial_width * 2, cards_position_Y, partial_width, button_height * card_scaler, True)
        # other buttons
        # if NOT active and NOT hover
        if not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X - partial_width * 1, difficulty_Y, partial_width, difficulty_height): # normal
            button_card_normal.draw_fixed_size(center_X - partial_width + card_position_smalling, cards_position_Y, partial_width * card_smalling, button_height * card_scaler, True)
        if not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 0, difficulty_Y, partial_width, difficulty_height): # hard
            button_card_hard.draw_fixed_size(center_X + card_position_smalling, cards_position_Y, partial_width * card_smalling, button_height * card_scaler, True)
        if not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 1, difficulty_Y, partial_width, difficulty_height): # extreme
            button_card_extreme.draw_fixed_size(center_X + partial_width + card_position_smalling, cards_position_Y, partial_width * card_smalling, button_height * card_scaler, True)
        if not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 2, difficulty_Y, partial_width, difficulty_height): # custom
            button_card_custom.draw_fixed_size(center_X + partial_width * 2 + card_position_smalling, cards_position_Y, partial_width * card_smalling, button_height * card_scaler, True)
        # if NOT active and HOVER
        if engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X - partial_width * 1, difficulty_Y, partial_width, difficulty_height): # normal
            button_card_normal.draw_fixed_size(center_X - partial_width + card_hover_position_smalling, cards_position_Y, partial_width * card_hover_smalling, button_height * card_scaler, True)
        if engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 0, difficulty_Y, partial_width, difficulty_height): # hard
            button_card_hard.draw_fixed_size(center_X + card_hover_position_smalling, cards_position_Y, partial_width * card_hover_smalling, button_height * card_scaler, True)
        if engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 1, difficulty_Y, partial_width, difficulty_height): # extreme
            button_card_extreme.draw_fixed_size(center_X + partial_width + card_hover_position_smalling, cards_position_Y, partial_width * card_hover_smalling, button_height * card_scaler, True)
        if engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 2, difficulty_Y, partial_width, difficulty_height): # custom
            button_card_custom.draw_fixed_size(center_X + partial_width * 2 + card_hover_position_smalling, cards_position_Y, partial_width * card_hover_smalling, button_height * card_scaler, True)
    if difficulty == "normal":
        # if ACTIVE
        button_card_normal.draw_fixed_size(center_X - partial_width, cards_position_Y, partial_width, button_height * card_scaler, True)
        # other buttons
        # if NOT active and NOT hover
        if not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X - partial_width * 2, difficulty_Y, partial_width, difficulty_height): # easy
            button_card_easy.draw_fixed_size(center_X - partial_width * 2 + card_position_smalling, cards_position_Y, partial_width * card_smalling, button_height * card_scaler, True)
        if not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 0, difficulty_Y, partial_width, difficulty_height): # hard
            button_card_hard.draw_fixed_size(center_X + card_position_smalling, cards_position_Y, partial_width * card_smalling, button_height * card_scaler, True)
        if not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 1, difficulty_Y, partial_width, difficulty_height): # extreme
            button_card_extreme.draw_fixed_size(center_X + partial_width + card_position_smalling, cards_position_Y, partial_width * card_smalling, button_height * card_scaler, True)
        if not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 2, difficulty_Y, partial_width, difficulty_height): # custom
            button_card_custom.draw_fixed_size(center_X + partial_width * 2 + card_position_smalling, cards_position_Y, partial_width * card_smalling, button_height * card_scaler, True)
        # if NOT active and HOVER
        if engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X - partial_width * 2, difficulty_Y, partial_width, difficulty_height): # easy
            button_card_easy.draw_fixed_size(center_X - partial_width * 2 + card_hover_position_smalling, cards_position_Y, partial_width * card_hover_smalling, button_height * card_scaler, True)
        if engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 0, difficulty_Y, partial_width, difficulty_height): # hard
            button_card_hard.draw_fixed_size(center_X + card_hover_position_smalling, cards_position_Y, partial_width * card_hover_smalling, button_height * card_scaler, True)
        if engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 1, difficulty_Y, partial_width, difficulty_height): # extreme
            button_card_extreme.draw_fixed_size(center_X + partial_width + card_hover_position_smalling, cards_position_Y, partial_width * card_hover_smalling, button_height * card_scaler, True)
        if engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 2, difficulty_Y, partial_width, difficulty_height): # custom
            button_card_custom.draw_fixed_size(center_X + partial_width * 2 + card_hover_position_smalling, cards_position_Y, partial_width * card_hover_smalling, button_height * card_scaler, True)
    if difficulty == "hard":
        # if ACTIVE
        button_card_hard.draw_fixed_size(center_X, cards_position_Y, partial_width, button_height * card_scaler, True)
        # other buttons
        # if NOT active and NOT hover
        if not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X - partial_width * 2, difficulty_Y, partial_width, difficulty_height): # easy
            button_card_easy.draw_fixed_size(center_X - partial_width * 2 + card_position_smalling, cards_position_Y, partial_width * card_smalling, button_height * card_scaler, True)
        if not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X - partial_width * 1, difficulty_Y, partial_width, difficulty_height): # normal
            button_card_normal.draw_fixed_size(center_X - partial_width + card_position_smalling, cards_position_Y, partial_width * card_smalling, button_height * card_scaler, True)
        if not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 1, difficulty_Y, partial_width, difficulty_height): # extreme
            button_card_extreme.draw_fixed_size(center_X + partial_width + card_position_smalling, cards_position_Y, partial_width * card_smalling, button_height * card_scaler, True)
        if not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 2, difficulty_Y, partial_width, difficulty_height): # custom
            button_card_custom.draw_fixed_size(center_X + partial_width * 2 + card_position_smalling, cards_position_Y, partial_width * card_smalling, button_height * card_scaler, True)
        # if NOT active and HOVER
        if engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X - partial_width * 2, difficulty_Y, partial_width, difficulty_height): # easy
            button_card_easy.draw_fixed_size(center_X - partial_width * 2 + card_hover_position_smalling, cards_position_Y, partial_width * card_hover_smalling, button_height * card_scaler, True)
        if engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X - partial_width * 1, difficulty_Y, partial_width, difficulty_height): # normal
            button_card_normal.draw_fixed_size(center_X - partial_width + card_hover_position_smalling, cards_position_Y, partial_width * card_hover_smalling, button_height * card_scaler, True)
        if engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 1, difficulty_Y, partial_width, difficulty_height): # extreme
            button_card_extreme.draw_fixed_size(center_X + partial_width + card_hover_position_smalling, cards_position_Y, partial_width * card_hover_smalling, button_height * card_scaler, True)
        if engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 2, difficulty_Y, partial_width, difficulty_height): # custom
            button_card_custom.draw_fixed_size(center_X + partial_width * 2 + card_hover_position_smalling, cards_position_Y, partial_width * card_hover_smalling, button_height * card_scaler, True)
    if difficulty == "extreme":
        # if ACTIVE
        button_card_extreme.draw_fixed_size(center_X + partial_width, cards_position_Y, partial_width, button_height * card_scaler, True)
        # other buttons
        # if NOT active and NOT hover
        if not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X - partial_width * 2, difficulty_Y, partial_width, difficulty_height): # easy
            button_card_easy.draw_fixed_size(center_X - partial_width * 2 + card_position_smalling, cards_position_Y, partial_width * card_smalling, button_height * card_scaler, True)
        if not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X - partial_width * 1, difficulty_Y, partial_width, difficulty_height): # normal
            button_card_normal.draw_fixed_size(center_X - partial_width + card_position_smalling, cards_position_Y, partial_width * card_smalling, button_height * card_scaler, True)
        if not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 0, difficulty_Y, partial_width, difficulty_height): # hard
            button_card_hard.draw_fixed_size(center_X + card_position_smalling, cards_position_Y, partial_width * card_smalling, button_height * card_scaler, True)
        if not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 2, difficulty_Y, partial_width, difficulty_height): # custom
            button_card_custom.draw_fixed_size(center_X + partial_width * 2 + card_position_smalling, cards_position_Y, partial_width * card_smalling, button_height * card_scaler, True)
        # if NOT active and HOVER
        if engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X - partial_width * 2, difficulty_Y, partial_width, difficulty_height): # easy
            button_card_easy.draw_fixed_size(center_X - partial_width * 2 + card_hover_position_smalling, cards_position_Y, partial_width * card_hover_smalling, button_height * card_scaler, True)
        if engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X - partial_width * 1, difficulty_Y, partial_width, difficulty_height): # normal
            button_card_normal.draw_fixed_size(center_X - partial_width + card_hover_position_smalling, cards_position_Y, partial_width * card_hover_smalling, button_height * card_scaler, True)
        if engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 0, difficulty_Y, partial_width, difficulty_height): # hard
            button_card_hard.draw_fixed_size(center_X + card_hover_position_smalling, cards_position_Y, partial_width * card_hover_smalling, button_height * card_scaler, True)
        if engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 2, difficulty_Y, partial_width, difficulty_height): # custom
            button_card_custom.draw_fixed_size(center_X + partial_width * 2 + card_hover_position_smalling, cards_position_Y, partial_width * card_hover_smalling, button_height * card_scaler, True)
    if difficulty == "custom":
        # if ACTIVE
        button_card_custom.draw_fixed_size(center_X + partial_width * 2, cards_position_Y, partial_width, button_height * card_scaler, True)
        # other buttons
        # if NOT active and NOT hover
        if not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X - partial_width * 2, difficulty_Y, partial_width, difficulty_height): # easy
            button_card_easy.draw_fixed_size(center_X - partial_width * 2 + card_position_smalling, cards_position_Y, partial_width * card_smalling, button_height * card_scaler, True)
        if not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X - partial_width * 1, difficulty_Y, partial_width, difficulty_height): # normal
            button_card_normal.draw_fixed_size(center_X - partial_width + card_position_smalling, cards_position_Y, partial_width * card_smalling, button_height * card_scaler, True)
        if not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 0, difficulty_Y, partial_width, difficulty_height): # hard
            button_card_hard.draw_fixed_size(center_X + card_position_smalling, cards_position_Y, partial_width * card_smalling, button_height * card_scaler, True)
        if not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 1, difficulty_Y, partial_width, difficulty_height): # extreme
            button_card_extreme.draw_fixed_size(center_X + partial_width + card_position_smalling, cards_position_Y, partial_width * card_smalling, button_height * card_scaler, True)
        # if NOT active and HOVER
        if engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X - partial_width * 2, difficulty_Y, partial_width, difficulty_height): # easy
            button_card_easy.draw_fixed_size(center_X - partial_width * 2 + card_hover_position_smalling, cards_position_Y, partial_width * card_hover_smalling, button_height * card_scaler, True)
        if engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X - partial_width * 1, difficulty_Y, partial_width, difficulty_height): # normal
            button_card_normal.draw_fixed_size(center_X - partial_width + card_hover_position_smalling, cards_position_Y, partial_width * card_hover_smalling, button_height * card_scaler, True)
        if engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 0, difficulty_Y, partial_width, difficulty_height): # hard
            button_card_hard.draw_fixed_size(center_X + card_hover_position_smalling, cards_position_Y, partial_width * card_hover_smalling, button_height * card_scaler, True)
        if engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * 1, difficulty_Y, partial_width, difficulty_height): # extreme
            button_card_extreme.draw_fixed_size(center_X + partial_width + card_hover_position_smalling, cards_position_Y, partial_width * card_hover_smalling, button_height * card_scaler, True)

    if not hover_difficulty_button and not engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X, button_up, long_button_width, button_height):
        button_difficulty.draw_fixed_size(center_X, button_up, long_button_width, button_height, True)
        engine.color = colors.gray[0], colors.gray[1], colors.gray[2]
        engine.color = colors.gray[0], colors.gray[1], colors.gray[2]
        engine.color = colors.gray[0], colors.gray[1], colors.gray[2]
        engine.color = colors.gray[0], colors.gray[1], colors.gray[2]
        engine.draw_text("difficulty".upper(), center_X, button_up, True)

    elif engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X, difficulty_Y, long_button_width, difficulty_height):
        hover_difficulty_button = True

    if hover_difficulty_button:
        button_difficulty_hover.draw_fixed_size(center_X, button_up, long_button_width, button_height, True)
        if difficulty == "easy":    engine.color = colors.green[0], colors.green[1], colors.green[2]
        if difficulty == "normal":  engine.color = colors.blue[0], colors.blue[1], colors.blue[2]
        if difficulty == "hard":    engine.color = colors.orange[0], colors.orange[1], colors.orange[2]
        if difficulty == "extreme": engine.color = colors.red[0], colors.red[1], colors.red[2]
        if difficulty == "custom":  engine.color = colors.purple[0], colors.purple[1], colors.purple[2]
        engine.draw_text("click to pick".upper(), center_X, button_up, True)

    # if hover_difficulty_button and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X, difficulty_Y, long_button_width, difficulty_height): #perf
    #
    #     draw_cursor() #perf
    #
    # else: hover_difficulty_button = False #perf

def update_difficulty_button():
    """
    udates the positions and scale of the difficulty cards

    :return: the difficulty cards animated
    """
    # GLOBALS
    global cards_position_Y

    if hover_difficulty_button:
        if not cards_position_Y >= cards_max_Y:
            cards_position_Y += 1
        elif cards_position_Y > cards_max_Y:
            cards_position_Y = cards_max_Y

    elif not hover_difficulty_button:
        if not cards_position_Y <= button_up:
            cards_position_Y -= 1
        elif cards_position_Y < button_up:
            cards_position_Y = button_up

# BUTTON CLICK
def init_action_start(source: str):
    """
    runs code to start when clicking on the button
    can also be triggered in other ways

    :param source: the source
    options: key (not likely) or mouse button

    this function is for a custom button, so no parameter for knowing the position on the grid

    :return: -
    """
    engine.shape_mode = ShapeMode.CENTER

    if source == "MouseButton.LEFT" and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y,
            center_X, center_Y, engine.width * 0.7 - 40, engine.height * 0.1 - 20):
        # go from game state start to menu
        init_menu()
    
    elif source == " ":
        # go from game state start to menu
        init_menu()

def init_action_add_custom_word(mouse_button):
    engine.shape_mode = ShapeMode.CENTER
    if (mouse_button == "MouseButton.LEFT"
            and difficulty == "custom"
            and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, engine.width * 0.718, engine.height / 1.575, small_button_width // 5 * 4, button_height // 5 * 4)):
        add_custom_word(True)

def init_action_play(source: str, grid_position: int = -1):
    """
    runs code to play game when clicking on the button
    can also be triggered in other ways

    :param source: the source
    options: key (not likely) or mouse button

    :param grid_position: the position it this function gets triggered
    only needed if it gets triggered in mouse_pressed_events
    it contains the position of the key

    :return: -
    """
    engine.shape_mode = ShapeMode.CENTER

    if grid_position == -1: return # no mouse_click or key_press event has happened, so skip all code

    if source == "MouseButton.LEFT":
        if   grid_position == 1 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_left, button_up, medium_button_width, button_height):
            common.print_info("» PLAY «")

            sound.play_note("sol", 4, 4)
            sound.play_note("sol", 5, 4)

            init_play()
        elif grid_position == 2 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_right, button_up, medium_button_width, button_height):
            common.print_info("» PLAY «")

            sound.play_note("sol", 4, 4)
            sound.play_note("sol", 5, 4)

            init_play()
        elif grid_position == 3 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_left, button_down, medium_button_width, button_height):
            common.print_info("» PLAY «")

            sound.play_note("sol", 4, 4)
            sound.play_note("sol", 5, 4)

            init_play()
        elif grid_position == 4 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_right, button_down, medium_button_width, button_height):
            common.print_info("» PLAY «")

            sound.play_note("sol", 4, 4)
            sound.play_note("sol", 5, 4)

            init_play()

    elif source == "SPACE":
        common.print_info("» PLAY «")

        sound.play_note("sol", 4, 4)
        sound.play_note("sol", 5, 4)

        init_play()

def init_action_stop(source: str, grid_position: int = -1):
    """
    runs code to stop game when clicking on the button
    can also be triggered in other ways

    :param source: the source
    options: key (not likely) or mouse button

    :param grid_position: the position it this function gets triggered
    only needed if it gets triggered in mouse_pressed_events
    it contains the position of the key

    :return: -
    """
    engine.shape_mode = ShapeMode.CENTER

    if grid_position == -1: return # no mouse_click or key_press event has happened, so skip all code

    if source == "MouseButton.LEFT":
        if   grid_position == 1 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_left, button_up, medium_button_width, button_height):
            init_action_stop_code()
        elif grid_position == 2 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_right, button_up, medium_button_width, button_height):
            init_action_stop_code()
        elif grid_position == 3 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_left, button_down, medium_button_width, button_height):
            init_action_stop_code()
        elif grid_position == 4 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_right, button_down, medium_button_width, button_height):
            init_action_stop_code()

    elif source == "TAB":
        init_action_stop_code()

def init_action_stop_code():
    """
    the code

    :return: -
    """
    common.print_info("× STOP ×")

    sound.play_note("mi", 5, 4)
    sound.play_note("do", 4, 4)

    init_menu()

def init_action_difficulty():
    init_action_difficulty_code(-2, "easy",    "mi",   2)
    init_action_difficulty_code(-1, "normal",  "fa+",  2)
    init_action_difficulty_code(0, "hard",    "sol+", 2)
    init_action_difficulty_code(1, "extreme", "la+",  2)
    init_action_difficulty_code(2, "custom",  "do",   3)

def init_action_difficulty_code(partial_width_factor, mode, note, octave):
    global difficulty
    if hover_difficulty_button and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, center_X + partial_width * partial_width_factor, difficulty_Y, partial_width, difficulty_height):
        difficulty = mode
        sound.play_note(note, octave, 16)

def init_action_quit(source: str, grid_position: int = -1):
    """
    runs code to quit when clicking on the button
    can also be triggered in other ways

    :param source: the source
    options: key (not likely) or mouse button

    :param grid_position: the position it this function gets triggered
    only needed if it gets triggered in mouse_pressed_events
    it contains the position of the key

    :return: -
    """
    engine.shape_mode = ShapeMode.CENTER

    if grid_position == -1: return # no mouse_click or key_press event has happened, so skip all code

    if source == "MouseButton.LEFT":
        if   grid_position == 1 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_left, button_up, medium_button_width, button_height):
            init_action_quit_code()
        elif grid_position == 2 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_right, button_up, medium_button_width, button_height):
            init_action_quit_code()
        elif grid_position == 3 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_left, button_down, medium_button_width, button_height):
            init_action_quit_code()
        elif grid_position == 4 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_right, button_down, medium_button_width, button_height):
            init_action_quit_code()

    elif source == "ENTER" or source == "SPACE" or source == "BACKSPACE" or source == "TAB":
        init_action_quit_code()

def init_action_quit_code():
    """
    quit code

    :return: -
    """
    common.print_info("× QUIT ×")

    # pygame.mixer_music.fadeout(100)

    sound.play_note("mi", 5, 4)
    sound.play_note("do", 4, 4)

    init_start()

def init_action_resume(source: str, grid_position: int = -1):
    """
    runs code to resume when clicking on the button
    can also be triggered in other ways

    :param source: the source
    options: key (not likely) or mouse button

    :param grid_position: the position it this function gets triggered
    only needed if it gets triggered in mouse_pressed_events
    it contains the position of the key

    :return: -
    """
    engine.shape_mode = ShapeMode.CENTER

    if grid_position == -1: return # no mouse_click or key_press event has happened, so skip all code

    if source == "MouseButton.LEFT":
        if   grid_position == 1 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_left, button_up, medium_button_width, button_height):
            init_action_resume_code()
        elif grid_position == 2 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_right, button_up, medium_button_width, button_height):
            init_action_resume_code()
        elif grid_position == 3 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_left, button_down, medium_button_width, button_height):
            init_action_resume_code()
        elif grid_position == 4 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_right, button_down, medium_button_width, button_height):
            init_action_resume_code()

    elif source == "ENTER" or source == "SPACE" or source == "BACKSPACE" or source == "TAB":
        init_action_resume_code()

def init_action_resume_code():
    global game_state
    common.print_info("= RESUME =")

    # pygame.mixer_music.play(loops=-1, start=-1000, fade_ms=100)

    sound.play_note("sol", 4, 4)
    sound.play_note("sol", 5, 4)

    game_state = GameState.PLAY

def init_action_giveup(source: str, grid_position: int = -1):
    """
    runs code to give up when clicking on the button
    can also be triggered in other ways

    :param source: the source
    options: key (not likely) or mouse button

    :param grid_position: the position it this function gets triggered
    only needed if it gets triggered in mouse_pressed_events
    it contains the position of the key

    :return: -
    """
    engine.shape_mode = ShapeMode.CENTER

    if grid_position == -1: return # no mouse_click or key_press event has happened, so skip all code

    if source == "MouseButton.LEFT":
        if   grid_position == 1 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_left, button_up, medium_button_width, button_height):
            init_action_giveup_code()
        elif grid_position == 2 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_right, button_up, medium_button_width, button_height):
            init_action_giveup_code()
        elif grid_position == 3 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_left, button_down, medium_button_width, button_height):
            init_action_giveup_code()
        elif grid_position == 4 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_right, button_down, medium_button_width, button_height):
            init_action_giveup_code()

    elif source == "BACKSPACE":
        init_action_giveup_code()

def init_action_giveup_code():
    """
    give up code

    :return: -
    """
    global game_state
    global transition_out

    common.print_info("¬ give up -")

    sound.play_note("mi", 4, 4)
    sound.play_note("do", 3, 4)

    transition_out = True

    # pygame.mixer_music.play(loops=-1, start=-1000, fade_ms=100)

    game_state = GameState.RESULT

def init_action_restart(source: str, grid_position: int = -1):
    """
    runs code to restart when clicking on the button
    can also be triggered in other ways

    :param source: the source
    options: key (not likely) or mouse button

    :param grid_position: the position it this function gets triggered
    only needed if it gets triggered in mouse_pressed_events
    it contains the position of the key

    :return: -
    """
    engine.shape_mode = ShapeMode.CENTER

    if grid_position == -1: return # no mouse_click or key_press event has happened, so skip all code

    if source == "MouseButton.LEFT":
        if   grid_position == 1 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_left, button_up, medium_button_width, button_height):
            init_action_restart_code()
        elif grid_position == 2 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_right, button_up, medium_button_width, button_height):
            init_action_restart_code()
        elif grid_position == 3 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_left, button_down, medium_button_width, button_height):
            init_action_restart_code()
        elif grid_position == 4 and engine.colliding_pointinrect(engine.mouse_x, engine.mouse_y, justify_button_right, button_down, medium_button_width, button_height):
            init_action_restart_code()

    elif source == "ENTER" or source == "SPACE" or source == "BACKSPACE" or source == "TAB":
        init_action_restart_code()

def init_action_restart_code():
    """
    restart code

    :return: -
    """
    common.print_info("¤ restart ¤")

    # pygame.mixer_music.fadeout(100)
    # pygame.mixer_music.play(loops=-1, start=-1000, fade_ms=100)

    sound.play_note("sol", 3, 4)
    sound.play_note("sol", 4, 4)

    init_play()


# STATE MENU's
def menu_options():
    """
    draw's the start menu with text and others

    :return: -
    """
    if suggest_difficulty == "easy":    suggest_color = (colors.green[0], colors.green[1], colors.green[2])
    if suggest_difficulty == "normal":  suggest_color = (colors.blue[0], colors.blue[1], colors.blue[2])
    if suggest_difficulty == "hard":    suggest_color = (colors.orange[0], colors.orange[1], colors.orange[2])
    if suggest_difficulty == "extreme": suggest_color = (colors.red[0], colors.red[1], colors.red[2])
    if suggest_difficulty == "custom":  suggest_color = (colors.purple[0], colors.purple[1], colors.purple[2])
    if difficulty == "easy":         difficulty_color = (colors.green[0], colors.green[1], colors.green[2])
    if difficulty == "normal":       difficulty_color = (colors.blue[0], colors.blue[1], colors.blue[2])
    if difficulty == "hard":         difficulty_color = (colors.orange[0], colors.orange[1], colors.orange[2])
    if difficulty == "extreme":      difficulty_color = (colors.red[0], colors.red[1], colors.red[2])
    if difficulty == "custom":       difficulty_color = (colors.purple[0], colors.purple[1], colors.purple[2])

    top_color   = "light"
    side_color  = "neutral"
    title       = "start menu"
    sub_title   = f"Welcome to: {game_title}"
    text_left   = ("Ah man, so many options to chose from", "", "I suggest picking:", "", "Turn the music on", "", "get ready to play!", "", "choose difficulty:")
    text_right  = ("", "", f"{suggest_difficulty}", "", "", "", "", "", f"{difficulty}")
    color_left  = (colors.white,)
    color_right = (
    colors.white, colors.white, suggest_color, colors.white, colors.white, colors.white, colors.white, colors.white, difficulty_color)

    draw_menu(top_color, side_color, title, sub_title, text_left, text_right, color_left, color_right)

    if difficulty == "custom":
        textarea_custom_word_input()

    # buttons
    draw_difficulty_button() # is custom button
    draw_M_button(3, "red", "quit")
    draw_M_button(4, "blue", "play game")

def menu_pause():
    """
    draw's the pause menu with text and buttons
    only drawable when you are in the state 'play'

    :return: -
    """
    top_color = "neutral"
    side_color = "normal"
    title = "pauze"
    sub_title = f"What do you want to do? "
    text_left = ("",)
    text_right = ("",)
    color_left = (colors.white,)
    color_right = (colors.white,)

    draw_menu(top_color, side_color, title, sub_title, text_left, text_right, color_left, color_right)

    # buttons
    draw_M_button(1, "purple", "give up")
    draw_M_button(2, "orange", "restart")
    draw_M_button(3, "green", "start menu")
    draw_M_button(4, "blue", "resume")

def menu_results():
    """
    draw's the start menu with text and others

    :return: -
    """
    if difficulty == "easy":         difficulty_color = (colors.green[0], colors.green[1], colors.green[2])
    if difficulty == "normal":       difficulty_color = (colors.blue[0], colors.blue[1], colors.blue[2])
    if difficulty == "hard":         difficulty_color = (colors.orange[0], colors.orange[1], colors.orange[2])
    if difficulty == "extreme":      difficulty_color = (colors.red[0], colors.red[1], colors.red[2])
    if difficulty == "custom":       difficulty_color = (colors.purple[0], colors.purple[1], colors.purple[2])

    top_color = "dark"
    side_color = "neutral"
    title = "results"
    sub_title = f"game over!"
    text_left = ("score:", "end time:", "", "right words:", "right letters:", "", "wrong words:", "wrong letters:", "played difficulty:")
    if converted_clock[2] == 60:
        converted_clock[2] =  0
        converted_clock[1] += 1
    text_right = (f"{round(total_score, 2)}".upper(), f"{converted_clock[0]}:{converted_clock[1]}:{converted_clock[2]}".upper(), "",
                  f"{total_right_words_score}".upper(), f"{total_right_letters_score}".upper(), "",
                  f"{score_wrong_words}".upper(), f"{score_wrong_letters}".upper(), f"{difficulty}".upper())
    color_left = ()
    color_right = (
    colors.orange, colors.l_purple1, colors.white, colors.green, colors.l_green, colors.white, colors.red, colors.l_red, difficulty_color)

    draw_menu(top_color, side_color, title, sub_title, text_left, text_right, color_left, color_right)

    # buttons
    draw_M_button(3, "red", "quit")
    draw_M_button(4, "blue", "start menu")


def scale_start_objects():
    """
    runs scale animation with start play button parameters

    :return: the animation play button size
    """
    global animation_play_size, animation_play_direction

    animation_play_size, animation_play_direction = scale_animation(animation_play_size, animation_play_direction, 0.1)


# ANIMATIONS
def scale_animation(value: float = 1, scale_direction: str = "+", scaler_range: float = 0.1) -> tuple:
    """
    Scale animation for images, that make them bigger and smaller accordion like.

    :param scaler_range: is
    :return: a scaler based around 1, that has a range of parameter scaler_range
    """
    # scaler_frames = scaler_range / engine.fps #perf
    #
    # scaler_min = 1 - scaler_range #perf
    # scaler_max = 1 + scaler_range #perf
    #
    # # if scaler reaches minimum / maximum, reverse scale_direction #perf
    # if value <= scaler_min: scale_direction = "+" #perf
    # if value >= scaler_max: scale_direction = "-" #perf
    #
    # # assigning the new scale direction #perf
    # if scale_direction == "+": value += scaler_frames #perf
    # if scale_direction == "-": value -= scaler_frames #perf

    return value, scale_direction

# transition
def game_transition_in():
    """
    transition to black
    :return: transition screen to black
    """
    global background_transition_alpha
    global transition_in, transition_out

    engine.color = 0, 0, 0, background_transition_alpha

    if transition_in:
        engine.outline_color = 0, 0, 0

        if background_transition_alpha >= 1:
            background_transition_alpha = 1
            transition_in = False
        else: background_transition_alpha += engine.fps / 60

        engine.shape_mode = ShapeMode.CENTER
        engine.draw_rectangle(engine.width / 2, engine.height / 2, engine.width, engine.height, 0)

def game_transition_out():
    """
    transition to black
    :return: transition screen to black
    """
    global background_transition_alpha
    global transition_in, transition_out

    engine.color = 0, 0, 0, background_transition_alpha

    if transition_out:
        engine.outline_color = 0, 0, 0

        if background_transition_alpha <= 0:
            background_transition_alpha = 0
            transition_out = False
        else: background_transition_alpha -= engine.fps / 60

        engine.shape_mode = ShapeMode.CENTER

        engine.draw_rectangle(center_X, center_Y, engine.width, engine.height, 0)

# STATES
class GameState(Enum):
    """
    all the states for the game
    """
    # most logical states order
    # 1) LOADING
    # 2) START
    # 3) MENU
    # 4) PLAY
    # 5) PAUSE
    # 6) GAME_OVER
    # 7) RESULT

    # loading screen
    LOADING = 0

    # begin screen
    START  = 1

    # menu's
    MENU   = 2 # gameplay setting menu
    RESULT = 6 # end results after playing the game
    PAUSE  = 4 # pause menu, where you can choose to
    # resume game » PLAY
    # quit game » START
    # giving up » RESULT
    # go back » MENU

    PLAY   = 3 # playing the actual game
    GAME_OVER = 5

def init_start():
    """
    game state switches to start

    Goes automatically after loading big resources like images, and image sequences to the options menu
    Is used when clicking on the play button in the options menu
    - game_state.loading »»» game_state.start

    :return:
    """
    pass

def init_loading() -> bool:
    """
    game state is loading

    has a purpose other than esthetics,
    and keeping users wait,
    but I made it to let Users know that the game is preparing,
    instead of a black screen where users kan think it doesn't work

    seen when loading content

    :return: initiate loading sequence,
    """
    global game_state, loading, loading_time
    global player_image_collection, player_image

    if game_state == GameState.LOADING:
        prepare_image_sequence("R", "SUF")

    return True

def init_menu():
    """
    game state to game options

    Is used when clicking on the click to start button
    - game_state.start »»» game_state.options

    :return: game state »»» game options
    """
    global game_state
    global suggest_difficulty
    global transition_in

    transition_in = True

    suggest_difficulty = random.choice(word_collections.difficulty_collection_titles)

    start_game_music()

    game_state = GameState.MENU

def init_play():
    """
    game state switches to play game

    Is used when clicking on the play button in the options menu
    or used when clicking on  restart button in the  pause  menu
    - game_state.start »»» game_state.options

    :return: game state »»» play game
    """
    global game_state
    global suggest_difficulty

    reset()

    suggest_difficulty = random.choice(word_collections.difficulty_collection_titles)

    game_state = GameState.PLAY

    setup_difficulty()

def init_start():
    """
    game state switches to stop
    it clears the words in main_word_collection

    Is used when clicking on the stop button in the options menu
    - game_state.options_menu »»» game_state.start

    :return: game state »»» stop
    """
    global game_state
    global main_word_collection
    global subtitle, suggest_difficulty

    # clear all the words
    main_word_collection.clear()

    stop_game_music()

    subtitle = random.choice(subtitle_choices)
    suggest_difficulty = random.choice(word_collections.difficulty_collection_titles)

    game_state = GameState.START

def reset():
    """
    resets all relevant game play value's to default

    :return: reseted relevant game play settings
    """
    # TITLES
    global subtitle
    subtitle = random.choice(subtitle_choices)

    # SCORES
    global total_score, current_score
    global total_right_words_score, total_right_letters_score, total_wrong_words_score, total_wrong_letters_score
    global score_right_words, score_right_letters, score_wrong_words, score_wrong_letters, save_score_wrong_letter
    total_score = 0  # your max score per game, it saves current value if current is bigger your end score
    current_score = 0  # the current_score, if it's <= 0, it's game over, time bites on this value so be careful

    total_right_words_score = 0
    total_right_letters_score = 0
    total_wrong_words_score = 0
    total_wrong_letters_score = 0

    score_right_words = 0
    score_right_letters = 0
    score_wrong_words = 0
    score_wrong_letters = 0
    save_score_wrong_letter = 0


    # WORDS
    global active_words, active_words_positions, word_generate_speed, word_fall_speed
    global max_words, word_fall_speed_max, word_speed_increase
    global difficulty, suggest_difficulty

    active_words.clear()
    active_words_positions.clear()

    max_words = 10000
    word_fall_speed = 1 * (engine.height / (general_scale * aspect_ratio[1]))
    word_fall_speed_max = 1.333 * word_fall_speed
    word_speed_increase = 0.001
    word_generate_speed = 3 + 3 * word_speed_increase

    suggest_difficulty = random.choice(word_collections.difficulty_collection_titles)
    # suggests a difficulty as an extra on the first menu


    # KEYBOARD input variables
    global target_key, save_key, target_word
    target_key = str()
    save_key = str()
    target_word = -1


    # COUNTERS
    global frames_counter, play_clock, converted_clock, play_total_time, play_counter_hour, play_counter_min, play_counter_sec, play_counter_sec_fps, play_word_counter

    frames_counter = 0
    play_clock = [0, 0, 0]
    converted_clock = [0, 0, 0]
    play_total_time = [0, 0, 0]
    play_counter_hour = 0
    play_counter_min = 0
    play_counter_sec = 0
    play_counter_sec_fps = 0
    play_word_counter = 0


    # PLAYER IMAGE
    global player_image, player_angle

    player_image = engine.load_image("spaceship/ship90.png")
    player_angle = 90


    # BULLETS $ FLARES
    global projectile_size

    projectile_size = 5

    # BULLETS (letter mining) & (firring missiles)
    global bullet_direction, bullet_unit_vector, bullet_vector_length, bullet_normalized_vector
    global bullet_speed
    global bullet_converted_vector, bullet_converted_velocity, bullet_color

    bullet_direction          = tuple()
    bullet_unit_vector        = tuple()
    bullet_vector_length      = tuple()
    bullet_normalized_vector  = tuple()

    bullet_speed              = 3

    bullet_converted_vector   = list()
    bullet_converted_velocity = list()
    bullet_color              = list()

    # FLARE (letter losing)
    global flare_direction, flare_unit_vector, flare_vector_length, flare_normalized_vector
    global flare_speed, flare_duration
    global flare_points_collection, flare_timer
    global flare_converted_vector, flare_converted_velocity, flare_color

    flare_direction           = tuple()
    flare_unit_vector         = tuple()
    flare_vector_length       = tuple()
    flare_normalized_vector   = tuple()

    flare_speed               = 3 # the speed
    flare_duration            = 0.3 * engine.fps

    flare_points_collection   = list()
    flare_timer               = list()

    flare_converted_vector    = list()
    flare_converted_velocity  = list()
    flare_color               = list()



# ENGINE functions
game_state = GameState.LOADING

async def setup():
    """
    Only executed ONCE (at the start); use to load files and initialize.
    """
    global player_image
    player_image = engine.load_image("spaceship/ship90.png")

    # gets random star positions
    setup_position_stars()

    pass

async def render():
    """
    This function is being executed over and over, as fast as the frame rate. Use to draw (not update).
    """
    global game_state
    global image_collection_init_done, image_collection_loaded_all

    match    game_state:
        case GameState.LOADING:
            draw_loading() # draw's loading screen when loading images and such
            if not image_collection_init_done: image_collection_init_done = init_loading()
            if image_collection_loaded_all:
                common.print_info(f"{colors.get_colored_text("===== " * 5, 'light gray')}", sep="", end="\n\n")
                game_state = GameState.START
            else: image_collection_loaded_all = load_image_sequence()

        case GameState.START:
            # background
            draw_background((0, 0, 0), 0)
            draw_stars()

            # main

            draw_start_screen()
            
            hover_start()

        case GameState.MENU:
            # background
            draw_background((0, 0, 0), 0.01)

            # main
            menu_options()

        case GameState.PLAY:
            # background
            draw_stars()
            draw_flare()
            draw_bullet()
            draw_background((0, 0, 0), 0.2)

            # main
            draw_target()
            draw_player()
            draw_words()
            draw_score()

        case GameState.RESULT:
            # background
            draw_background((0, 0, 0), 0.01)

            # main
            menu_results()

        case GameState.PAUSE:
            # background
            engine.background_color = 0, 0, 0

            # main
            menu_pause()

async def evaluate():
    """
    This function is being executed over and over, as fast as the frame rate. Use to update (not draw).
    """
    global frames_counter, test_print_update_counter

    match    game_state:
        case GameState.LOADING:
            update_loading()

        case GameState.START:
            # background
            # update_stars() #perf

            # main
            # scale_start_objects() #perf
            pass

        case GameState.MENU:
            # background
            # update_stars()

            # buttons
            update_difficulty_button()

        case GameState.PLAY:
            # background
            # update_stars() #perf
            update_second_timer()

            # main
            update_bullet()
            update_flare()
            # move_player()
            rotate_player()
            get_words()
            update_words()
            check_words()

            calc_score()

            frames_counter += 1

    check_bullet()
    check_flare()

    # transitions
    # game_transition_in() #perf
    # game_transition_out() #perf

async def mouse_pressed_event(mouse_x: int, mouse_y: int, mouse_button: MouseButton):
    """
    This function is only executed once each time a mouse button was pressed!
    """
    global game_state
    global difficulty

    match    game_state:
        case GameState.START:
            init_action_start(str(mouse_button))

        case GameState.MENU:
            # custom text_area input button
            init_action_add_custom_word(str(mouse_button))

            # difficulty button
            init_action_difficulty()

            # quit button
            init_action_quit(str(mouse_button), 3)

            # play button
            init_action_play(str(mouse_button), 4)

        case GameState.PLAY:
            # for shooting a projectile
            if mouse_button == MouseButton.LEFT:
                add_bullet((engine.mouse_x, engine.mouse_y), (player_position_X, player_position_Y), colors.blue)
                sound.play_note("fa", 5, 32) # sound for firing a bullet

        case GameState.PAUSE:
            engine.shape_mode = ShapeMode.CENTER

            init_action_giveup(str(mouse_button), 1)
            init_action_restart(str(mouse_button), 2)
            init_action_stop(str(mouse_button), 3)
            init_action_resume(str(mouse_button), 4)

        case GameState.RESULT:
            engine.shape_mode = ShapeMode.CENTER

            init_action_stop(str(mouse_button), 3)
            init_action_restart(str(mouse_button), 4)

async def key_down_event(key: str):
    """
    This function is only executed once each time a key was released!
    Special keys have more than 1 character, for example ESCAPE, BACKSPACE, ENTER, ...
    """
    # move player toggle
    global game_state, transition_in
    global target_key, save_key

    if game_state == GameState.START:
        
        init_action_start(key)

    if game_state == GameState.MENU:
        if difficulty == "custom": add_custom_word(key)

    if game_state == GameState.PLAY:
        if key == "LEFT": player_moving = -1
        else: player_moving = 0

        if key == "RIGHT": player_moving = 1
        else: player_moving = 0

        if key in "abcdefghijklmnopqrstuvwxyz -'`.0123456789":
            if save_key == key:
                save_key = None
            target_key = key

            # !!! work around
            global score_wrong_letters, save_score_wrong_letter
            save_score_wrong_letter = score_wrong_letters
            score_wrong_letters += 1
            # until here

            sound.play_note("si", 4, 32)

async def key_up_event(key: str):
    """
    This function is only executed once each time a key was released!
    Special keys have more than 1 character, for example ESCAPE, BACKSPACE, ENTER, ...
    """
    # game states switch
    global game_state

    if key == "ESCAPE" and game_state == GameState.PLAY:
        # pygame.mixer_music.fadeout(200)

        game_state = GameState.PAUSE
    elif "ESCAPE" and game_state == GameState.PAUSE:
        # pygame.mixer_music.play(loops=-1, start=-1000, fade_ms=200)

        game_state = GameState.PLAY

    # move player toggle
    global player_moving

    if game_state == GameState.PLAY:
        if key == "LEFT": player_moving = 0
        if key == "RIGHT": player_moving = 0

        pass
    pass

# Engine stuff; best not to mess with this:
engine._setup = setup
engine._evaluate = evaluate
engine._render = render
engine._mouse_pressed_event = mouse_pressed_event
engine._key_down_event = key_down_event
engine._key_up_event = key_up_event

# # Start the game loop:
# engine.play()