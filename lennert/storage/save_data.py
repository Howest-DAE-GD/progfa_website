from typing import List
from typing import Any
from dataclasses import dataclass
import json

@dataclass
class Score:
    total: int
    words_correct: int
    letters_correct: int
    words_fault: int
    letters_fault: int
    time: str
    difficulty: str
    highs_core: int

    @staticmethod
    def from_dict(obj: Any) -> 'Score':
        _total = int(obj.get("total"))
        _words_correct = int(obj.get("words_correct"))
        _letters_correct = int(obj.get("letters_correct"))
        _words_fault = int(obj.get("words_fault"))
        _letters_fault = int(obj.get("letters_fault"))
        _time = str(obj.get("time"))
        _difficulty = str(obj.get("difficulty"))
        _highs_core = int(obj.get("highs_core"))
        return Score(_total, _words_correct, _letters_correct, _words_fault, _letters_fault, _time, _difficulty, _highs_core)

@dataclass
class Player:
    name: str
    score: Score

    @staticmethod
    def from_dict(obj: Any) -> 'Player':
        _name = str(obj.get("name"))
        _score = Score.from_dict(obj.get("score"))
        return Player(_name, _score)

@dataclass
class Save_data:
    players: List[Player]

    @staticmethod
    def from_dict(obj: Any) -> 'Save_data':
        _players = [Player.from_dict(y) for y in obj.get("players")]
        return Save_data(_players)

    def toJSON(self):
        return json.dumps(self, default=lambda o:o.__dict__, sort_keys=True, indent=2)
