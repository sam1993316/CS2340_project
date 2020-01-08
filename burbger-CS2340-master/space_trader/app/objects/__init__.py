from random import random, randint
from random import choice as randchoice
from enum import IntEnum
from flask import render_template
from .items import clean_items
from .universe import Universe
from .character import Player
from .borg import Borg


class Game(Borg):
    _shared_state = {}
    _difficulty_names = ['Easy', 'Medium', 'Hard']

    def __init__(self):
        Borg.__init__(self)

    @classmethod
    def new(cls, player_info, difficulty):
        # pylint: disable=protected-access, attribute-defined-outside-init
        new_game = cls()
        new_game._difficulty = difficulty

        money = 1000 - (500 * difficulty)
        if money == 0:
            money = 100

        clean_items()
        universe = Universe.new()
        Player.new(*player_info, money, randchoice(universe.regions))
        victory_region = randchoice(universe.regions)
        victory_region.marketplace.add_winning_item(victory_region, Player())

        return new_game

    def __delete__(self, deleted):
        print("Cleaned up Game reference:", deleted)

    @property
    def difficulty(self):
        return self._difficulty

    @property
    def difficulty_name(self):
        return self._difficulty_names[self._difficulty]
