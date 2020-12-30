"""Client module for controlling game progression"""
from typing import Sequence
from itertools import cycle
from random import randint

import attr

from clovek_ne_jezi_se.agent import Player
from clovek_ne_jezi_se.game_state import EMPTY_SYMBOL, GameState


@attr.s
class Client:
    """
    Client class for controlling game flow.
    """
    players = attr.ib(type=Sequence['Player'])
    pieces_per_player = attr.ib(kw_only=True, type=int, default=4)
    main_board_section_length = attr.ib(kw_only=True, type=int, default=10)
    number_of_dice_faces = attr.ib(
        kw_only=True, type=int, default=6
    )
    empty_symbol = attr.ib(kw_only=True, default=EMPTY_SYMBOL)

    def initialize(self):
        self._player_cycle = cycle(self.players)
        player_names = [player.name for player in self.players]
        self._game_state = GameState(
            player_names,
            pieces_per_player=self.pieces_per_player,
            section_length=self.main_board_section_length,
            number_of_dice_faces=self.number_of_dice_faces,
            empty_symbol=self.empty_symbol
        )

    def get_game_state(self):
        return self._game_state

    def next_player(self):
        return next(self._player_cycle)

    def roll(self):
        return randint(1, self.number_of_dice_faces)