#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 26/11/2024

@author: noreh
"""
import random

import progfa.progfa_engine as pfe
from progfa.progfa_image import ProgfaImage
from progfa.progfa_engine import ShapeMode, MouseButton

# import pygame.mixer


# Create an instance of ProgfaEngine and set window size (width, height):
engine = pfe.ProgfaEngine(1200, 600)

# Set the frame rate to x frames per second:
engine.set_fps(60)

# region IMAGES and MODES
# images
image_home = engine.load_image("Resources/homescreen.png")
image_home.resize(engine.width, engine.height, True)
image_game = engine.load_image("Resources/gameplayscreen.png")
image_game.resize(engine.width, engine.height, True)
image_receipt = engine.load_image("Resources/endscreen.png")
image_receipt.resize(450, 900)
image_scanner = engine.load_image("Resources/scanner.png")
image_scanner.resize(340, 500, False)
image_pause = engine.load_image("Resources/pausescreen.png")

# # sound effects
# type_sound = pygame.mixer.Sound("Resources/type.mp3")
# pop_sound = pygame.mixer.Sound("Resources/wordpop.mp3")
# mistake_sound = pygame.mixer.Sound("Resources/mistake.mp3")
# menu_sound = pygame.mixer.Sound("Resources/menu.mp3")
# ting_sound = pygame.mixer.Sound("Resources/ting.mp3")
# buzzer_sound = pygame.mixer.Sound("Resources/gameover.mp3")
# pygame.mixer.music.load("Resources/music.mp3")

# MODES
from enum import Enum


class GameState(Enum):
    START = 0
    GAMEPLAY = 1
    GAMEOVER = 2
    GAMEWON = 3
    PAUSE = 4


gamestate = GameState.START
# endregion

# region GLOBAL VARIABLES
# GLOBAL LISTS
easy_words = ["apple", "bridge", "candle", "dance", "energy", "flower", "garden", "helmet", "island", "jungle",
              "kitten", "ladder", "marble", "nature", "orange", "puzzle", "rabbit", "simple", "summer", "travel",
              "valley", "window", "yellow", "zebra", "bright", "clever", "damage", "effort", "gentle", "hunter",
              "jacket", "lemon", "market", "number", "ocean", "people", "quiet", "reward", "shadow", "ticket", "useful",
              "winner", "family", "forest", "picnic", "soccer", "turtle", "sunset", "winter", "animal", "basket",
              "castle", "driver", "editor", "farmer", "glider", "hockey", "impact", "jolly", "kindly", "loyal",
              "memory", "native", "planet", "quest", "reason", "singer", "target", "urgent", "violin", "wallet",
              "yearly", "beacon", "breeze", "copper", "desert", "feather", "goblet", "heater", "jumper", "keeper",
              "lantern", "mirror", "object", "pepper", "quiver", "ribbon", "safety", "tailor", "unique", "velvet",
              "whistle", "yonder", "zigzag"]
hard_words = ["adventure", "backpack", "brilliant", "chocolate", "discovery", "elephant", "fantastic", "generous",
              "hospital", "impossible", "jellyfish", "kilometer", "lemonade", "marathon", "notebook", "organize",
              "parachute", "question", "ridiculous", "signature", "telescope", "umbrella", "victorious", "whirlwind",
              "excitement", "fabulous", "generation", "historical", "incredible", "journalism", "knowledge",
              "literature", "magnificent", "necessity", "optimistic", "philosophy", "quarantine", "refreshing",
              "surprising", "tolerance", "universal", "volunteer", "watermelon", "xenophile", "youthful", "zoologist",
              "ambitious", "backfire", "complexity", "dangerous", "enormous", "fortitude", "gracious", "hurricane",
              "innovative", "judgmental", "kingfisher", "landslide", "masterpiece", "navigator", "objective",
              "persistent", "questionable", "resilience", "sophisticated", "trustworthy", "unpredictable", "versatile",
              "xenophobic", "yielding", "architecture", "bravery", "conqueror", "determined", "emergency",
              "flourishing", "grandiose", "hypothesis", "initiative", "justice", "leadership", "motivation",
              "nurturing", "opposition", "patience", "resourceful", "strategy", "tremendous", "uplifting", "visionary",
              "whimsical", "yearning", "zenithal"]
passed_words = []
typed_words = []
word_x = []

grocery_list = []
passed_groceries = []
grocery_x = []

score_history = []
mistake_history = []

# GLOBAL VARIABLES
difficulty = 0
word_difficulty = 0

typed_letters = 0

# TIMER TO SPAWN NEW GROCERY
counter = 120

# SCORE AND TIME
money = 0
lives = 5
timecounter = 0
time = 60
mistakes = 0

speed = 2.5
random_time = random.randint(160, 240)


# endregion


# region SETUP
async def setup():
    """
    Only executed ONCE (at the start); use to load files and initialize.
    """
    engine.set_font("Resources/Happy School.ttf")
    engine.set_font_size(40)

    # pygame.mixer.music.play(loops = -1)

    for index in range(1, 9):
        grocery: ProgfaImage = engine.load_image(f"Resources/grocery{index}.png")
        grocery.resize(230, 230)
        grocery_list.append(grocery)

    pass


# endregion

# ----------------------------------------------------------------------------------------------------------------------

# region HOMESCREEN
def draw_homescreen():
    """
    Draws the homescreen with the difficulties and score history
    :return:
    """
    # background
    engine.shape_mode = ShapeMode.CORNER
    image_home.draw(0, 0)  # _fixed_size(0, 0, engine.width, engine.height, True)

    # difficulty
    engine.shape_mode = ShapeMode.CENTER
    engine.color = 1, 1, 1

    if difficulty == 0:  # difficulty in speed
        engine.outline_color = 0.9, 0.45, 0.35
    engine.draw_rectangle(215, 335, 120, 40, 3)
    engine.outline_color = None
    if difficulty == 1:
        engine.outline_color = 0.9, 0.45, 0.35
    engine.draw_rectangle(353, 335, 120, 40, 3)
    engine.outline_color = None

    if word_difficulty == 0:  # difficulty in words
        engine.outline_color = 0.9, 0.45, 0.35
    engine.draw_rectangle(215, 425, 120, 40, 3)
    engine.outline_color = None
    if word_difficulty == 1:
        engine.outline_color = 0.9, 0.45, 0.35
    engine.draw_rectangle(353, 425, 120, 40, 3)
    engine.outline_color = None

    engine.color = 0.9, 0.45, 0.35
    engine.set_font_size(30)
    engine.draw_text("Easy", 182, 315)
    engine.draw_text("Hard", 316, 315)
    engine.draw_text("Easy", 182, 405)
    engine.draw_text("Hard", 316, 405)

    # score history
    engine.shape_mode = ShapeMode.CORNER
    engine.set_font_size(25)
    if 0 < len(mistake_history) <= 3:
        engine.draw_text(f"{score_history[0] : 03d}$ / {mistake_history[0]} mistakes", 800, 325)
    if 1 < len(mistake_history) <= 3:
        engine.draw_text(f"{score_history[1] : 03d}$ / {mistake_history[1]} mistakes", 800, 360)
    if 2 < len(mistake_history) <= 3:
        engine.draw_text(f"{score_history[2] : 03d}$ / {mistake_history[2]} mistakes", 800, 394)


# endregion

# region GAMEPLAY
def add_word():
    """
    This function adds a random word that will pass the screen to the passed_words list
    :return:
    """
    global passed_words

    if word_difficulty == 0:
        word = random.choice(easy_words)
        word_x.append(-150)
    if word_difficulty == 1:
        word = random.choice(hard_words)
        word_x.append(-200)

    passed_words.append(word)


def add_grocery():
    """
    This function adds a grocery to the list passed_groceries
    :return:
    """
    grocery = random.choice(grocery_list)
    passed_groceries.append(grocery)

    grocery_x.append(-150)


def draw_gameplay_background():
    """
    Draw background of gameplay
    :return:
    """
    engine.shape_mode = ShapeMode.CORNER
    image_game.draw(0, 0)  # _fixed_size(0, 0, engine.width, engine.height, True)
    engine.shape_mode = ShapeMode.CENTER
    engine.color = 0.83, 0.73, 0.7
    engine.draw_rectangle(1155, 400, 340, 500)


def draw_word(word, x):
    """
    This function draws the random word that slides along the x axis
    :return:
    """
    engine.shape_mode = ShapeMode.CORNER
    engine.set_font_size(40)

    engine.color = 0.6, 0.5, 0.5
    engine.draw_text(word, x + 3, (engine.height / 3) + 3)

    engine.color = 1, 1, 1
    engine.draw_text(word, x, engine.height / 3)

    if word == passed_words[0]:  # draws letters of first word green
        green_letters = word[:typed_letters]
        engine.color = 0.7, 1, 0.6
        engine.draw_text(green_letters, x, engine.height / 3)


def draw_grocery():
    """
    Make words and groceries slide on the screen
    :return:
    """
    engine.shape_mode = ShapeMode.CENTER

    # draw sliding groceries
    for index in range(0, len(passed_groceries)):
        passed_groceries[index].draw(grocery_x[index] + 60, (engine.height / 2) + 40)


def draw_scanner():
    """
    This function draws the scanner
    :return:
    """
    image_scanner.draw(1092, 400)  # _fixed_size(1092, 400, 340, 500, False)


def draw_gameplay_text():
    """
    draws the score and timer
    :return:
    """
    engine.color = 1, 1, 1
    engine.shape_mode = ShapeMode.CORNER
    engine.set_font_size(40)

    engine.draw_text(f"MONEY: {money: 03d}$", 40, 20)
    engine.draw_text(f"TIME: {time: 03d}s", 950, 20)


def draw_lives():
    """
    draws the lives of the user
    :return:
    """
    engine.color = 0.5, 0.5, 0.5
    engine.shape_mode = ShapeMode.CENTER
    engine.outline_color = None

    for index in range(0, 5):
        engine.draw_circle(520 + (40 * index), 30, 30, 5)

    engine.color = 0.7, 1, 0.6
    for index in range(0, lives):
        engine.draw_circle(520 + (40 * index), 30, 30, 5)


def draw_mistakes():
    """
    draws amount of mistakes made
    :return:
    """
    engine.color = 0.9, 0.45, 0.35
    engine.shape_mode = ShapeMode.CENTER
    engine.outline_color = None
    engine.set_font_size(25)
    engine.draw_text(f"Mistakes: {mistakes}", engine.width / 2, 62, True)


def draw_pausescreen():
    """
    draws the pause pop up menu when game is paused (escape)
    :return:
    """
    engine.shape_mode = ShapeMode.CENTER
    image_pause.draw(engine.width / 2, engine.height / 2)
    # _fixed_size(engine.width / 2, engine.height / 2, 500, 300, True)


# endregion

# region ENDSCREEN
def draw_endscreen():
    """
    Draws the end screen with reciept
    :return:
    """
    engine.shape_mode = ShapeMode.CORNER
    image_receipt.draw(engine.width / 2 - 228, 0)  # _fixed_size(engine.width / 2 - 228, 0, 450, 900)

    engine.shape_mode = ShapeMode.CENTER

    if gamestate == GameState.GAMEWON:
        engine.set_font_size(60)
        engine.color = 0.9, 0.45, 0.35
        engine.draw_text(f"Game Won", engine.width / 2, 210, True)

    if gamestate == GameState.GAMEOVER:
        engine.set_font_size(60)
        engine.color = 0.9, 0.45, 0.35
        engine.draw_text(f"Game Over", engine.width / 2, 210, True)

    engine.set_font_size(25)
    engine.color = 0.45, 0.4, 0.4
    engine.draw_text(f"Money: {money: 03d}$", engine.width / 2, 260, True)
    engine.draw_text(f"Mistakes: {mistakes}", engine.width / 2, 290, True)
    engine.draw_text(f"Lives left: {lives}", engine.width / 2, 320, True)

    engine.color = 0.45, 0.4, 0.4
    engine.set_font_size(30)
    engine.draw_text("Home", engine.width / 2 - 85, 435, True)
    engine.draw_text("Try again", engine.width / 2 + 85, 435, True)


# endregion

def reset_game():
    """
    resets all game parameters when called
    :return:
    """
    global typed_letters, money, lives, timecounter, time, counter, mistakes
    passed_words.clear()  # reset everything
    typed_words.clear()
    word_x.clear()
    passed_groceries.clear()
    grocery_x.clear()
    typed_letters = 0
    money = 0
    lives = 5
    timecounter = 0
    time = 60
    counter = 120
    mistakes = 0


# ----------------------------------------------------------------------------------------------------------------------

# region RENDER
async def render():
    """
    This function is being executed over and over, as fast as the frame rate. Use to draw (not update).
    """
    # START
    if gamestate == GameState.START:
        # Background
        draw_homescreen()

    # GAMEPLAY
    if gamestate == GameState.GAMEPLAY:
        draw_gameplay_background()

        draw_grocery()

        # Draw words
        for index, word in enumerate(passed_words):
            draw_word(word, word_x[index])

        draw_gameplay_text()

        draw_lives()

        draw_mistakes()

        draw_scanner()

    # PAUSE SCREEN
    if gamestate == GameState.PAUSE:
        draw_pausescreen()

    # END SCREEN
    if gamestate == GameState.GAMEWON or gamestate == GameState.GAMEOVER:
        draw_endscreen()

    engine.color = 1, 1, 1
    engine.set_font_size(15)
    engine.draw_text("Game by Nore Pollentier", 1002, 575)

    pass


# endregion

# region EVALUATE
async def evaluate():
    """
    This function is being executed over and over, as fast as the frame rate. Use to update (not draw).
    """
    global gamestate

    # GAMEPLAY
    if gamestate == GameState.GAMEPLAY:
        global counter, timecounter, time, lives, random_time, speed, typed_letters

        # add a word every few seconds
        counter += 1
        if counter == random_time:
            add_word()
            counter = 0
            add_grocery()
            if difficulty == 0:
                random_time = random.randint(160, 220)
            if difficulty == 1:
                random_time = random.randint(120, 180)

        # move words and groceries
        for index in range(0, len(passed_words)):
            word_x[index] += speed
        for index in range(0, len(passed_groceries)):
            grocery_x[index] += speed

        # time goes down
        timecounter += 1
        if timecounter == 60:
            timecounter = 0
            time -= 1

        # remove words from list
        if len(passed_groceries) >= 1 and len(word_x) >= 1:
            if (engine.width - 240) - 1 < word_x[0] < (engine.width - 240) + 3:
                word_x.pop(0)
                passed_words.pop(0)
                lives -= 1
                typed_letters = 0
            if grocery_x[0] >= engine.width:
                passed_groceries.pop(0)
                grocery_x.pop(0)

        # change to game over/won if
        if lives == 0:
            # pygame.mixer.Sound.play(buzzer_sound)
            gamestate = GameState.GAMEOVER
            mistake_history.append(mistakes)
            score_history.append(money)
        if time == 0:
            if money <= 0:
                # pygame.mixer.Sound.play(buzzer_sound)
                gamestate = GameState.GAMEOVER
                mistake_history.append(mistakes)
                score_history.append(money)
            else:
                # pygame.mixer.Sound.play(ting_sound)
                gamestate = GameState.GAMEWON
                mistake_history.append(mistakes)
                score_history.append(money)

    # Make sure only last 3 games are saved in mistake/score_history
    if len(mistake_history) == 4:
        mistake_history.pop(0)
        score_history.pop(0)

    pass


# endregion

# region MOUSE_PRESSED_EVENT
async def mouse_pressed_event(mouse_x: int, mouse_y: int, mouse_button: MouseButton):
    """
    This function is only executed once each time a mouse button was pressed!
    """
    global gamestate, typed_letters, money, lives, timecounter, time, counter, difficulty, word_difficulty, speed, random_time, mistakes

    # START
    if gamestate == GameState.START:
        # Start game
        if mouse_button == MouseButton.LEFT and (engine.width / 2) - 80 < mouse_x < (engine.width / 2) + 69 and (
                engine.height / 2) - 35 < mouse_y < (engine.height / 2) + 30:
            # pygame.mixer.Sound.play(ting_sound)
            gamestate = GameState.GAMEPLAY

        # Select difficulty
        engine.shape_mode = ShapeMode.CENTER
        if mouse_button == MouseButton.LEFT and engine.colliding_pointinrect(mouse_x, mouse_y, 215, 335, 120, 40):
            # pygame.mixer.Sound.play(menu_sound)
            difficulty = 0
            speed = 2.5
            random_time = random.randint(160, 220)
        if mouse_button == MouseButton.LEFT and engine.colliding_pointinrect(mouse_x, mouse_y, 353, 335, 120, 40):
            # pygame.mixer.Sound.play(menu_sound)
            difficulty = 1
            speed = 4
            random_time = random.randint(120, 180)

        # select word difficulty
        if mouse_button == MouseButton.LEFT and engine.colliding_pointinrect(mouse_x, mouse_y, 215, 425, 120, 40):
            # pygame.mixer.Sound.play(menu_sound)
            word_difficulty = 0
        if mouse_button == MouseButton.LEFT and engine.colliding_pointinrect(mouse_x, mouse_y, 353, 425, 120, 40):
            # pygame.mixer.Sound.play(menu_sound)
            word_difficulty = 1

    # PAUSE SCREEN
    if gamestate == GameState.PAUSE:
        # Continue
        if mouse_button == MouseButton.LEFT and engine.colliding_pointinrect(mouse_x, mouse_y, 711, 362, 193, 90):
            gamestate = GameState.GAMEPLAY
            # pygame.mixer.Sound.play(menu_sound)
        # Home
        if mouse_button == MouseButton.LEFT and engine.colliding_pointinrect(mouse_x, mouse_y, 490, 362, 193, 90):
            reset_game()
            # pygame.mixer.Sound.play(menu_sound)
            gamestate = GameState.START

    # GAME OVER/GAME WON
    if gamestate == GameState.GAMEWON or gamestate == GameState.GAMEOVER:
        # Home button
        if mouse_button == MouseButton.LEFT and engine.colliding_pointinrect(mouse_x, mouse_y, 512, 436, 160, 70):
            reset_game()
            # pygame.mixer.Sound.play(menu_sound)
            gamestate = GameState.START

        # Try again button
        if mouse_button == MouseButton.LEFT and engine.colliding_pointinrect(mouse_x, mouse_y, 685, 436, 160, 70):
            reset_game()
            # pygame.mixer.Sound.play(menu_sound)
            gamestate = GameState.GAMEPLAY

    pass


# endregion

# region KEY_UP_EVENT
async def key_up_event(key: str):
    """
    This function is only executed once each time a key was released!
    Special keys have more than 1 character, for example ESCAPE, BACKSPACE, ENTER, ...
    """
    global gamestate

    # IF LETTER IS TYPED: REMOVE LETTER FROM WORD
    if gamestate == GameState.GAMEPLAY:
        global typed_letters, money, lives, mistakes

        if len(passed_words) > 0:
            current_word = list(passed_words[0])
            if key == current_word[typed_letters]:  # count how many letters of word are typed
                typed_words.append(key)
                typed_letters += 1
                # pygame.mixer.Sound.play(type_sound)
            elif key == 'ESCAPE':
                pass
            else:
                # pygame.mixer.Sound.play(mistake_sound)
                money -= 5
                mistakes += 1

            if typed_letters == len(current_word):  # remove word if its typed
                passed_words.pop(0)
                word_x.pop(0)
                # pygame.mixer.Sound.play(pop_sound)

                money += 5
                typed_letters = 0

        # PAUSE
        if key == 'ESCAPE':
            # pygame.mixer.Sound.play(menu_sound)
            gamestate = GameState.PAUSE

    pass


# endregion

# Engine stuff; best not to mess with this:
engine._setup = setup
engine._evaluate = evaluate
engine._render = render
engine._mouse_pressed_event = mouse_pressed_event
engine._key_up_event = key_up_event
