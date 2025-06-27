"""
Created on 15/01/2025

 custom word collections

@author: Lennert
"""
import json

# GLOBALS
custom_word_generate_speed = 1
custom_word_fall_speed = 1
custom_word_fall_speed_max = 1

collections_json = None

def load_json_file() :
    global collections_json
    with open("storage/collections.json", "r") as collections_file:
        collections_json = json.load(collections_file)

    collections_file.close()


def get_collection(title: str) -> list:
    if collections_json is None: load_json_file()
    for collection in collections_json["default"]:
        if collection["title"] == title:
            return collection["collection"]
    return list()


def get_easter_egg(title: str) -> list:
    if collections_json is None: load_json_file()
    for collection in collections_json["easter_eggs"]:
        if collection["title"] == title:
            return collection["collection"]
    return list()


def get_easter_eggs() -> list:
    if collections_json is None: load_json_file()
    if len(easter_egg_collection_titles) < 1:
        for collection in collections_json["easter_eggs"]:
            easter_egg_collection_titles.append(collection["title"])
    return easter_egg_collection_titles


# DIFFICULTY
difficulty_collection_titles = ("easy", "normal", "hard", "extreme", "custom")

easy_word_collection = get_collection("easy")
normal_word_collection = get_collection("normal")
hard_word_collection = get_collection("hard")
extreme_word_collection = get_collection("extreme")

# ADD ONS for custom collections
easter_egg_collection_titles = list()
easter_egg_collection_words = list()
