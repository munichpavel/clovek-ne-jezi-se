"""Client module for controlling game progression"""
import logging
import os
from pathlib import Path

from typing import Sequence
from itertools import cycle
from random import randint

import attr

from clovek_ne_jezi_se.agents import Player
from clovek_ne_jezi_se.game_state import (
    EMPTY_SYMBOL, GameState
)


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
    verbose = attr.ib(default=False)

    def initialize(self):
        self._player_cycle = cycle(self.players)
        self._player_names = [player.name for player in self.players]
        self._game_state = GameState(
            self._player_names,
            pieces_per_player=self.pieces_per_player,
            section_length=self.main_board_section_length,
            number_of_dice_faces=self.number_of_dice_faces,
            empty_symbol=self.empty_symbol
        )
        self._game_state.initialize()
        self._winner = None
        if self.verbose:
            logging.basicConfig(
                filename=Path(os.environ['LOG_DIR']) / 'play.log',
                level=logging.DEBUG
            )

    def play(self):
        """Play until a player wins wins"""

        while(self._winner is None):
            self.take_turn()

    def take_turn(self):
        """Take a single player turn"""
        current_player = self.next_player()
        roll_value = self.roll()

        moves = self._game_state.get_player_moves(
            roll_value, current_player.name
        )
        if self.verbose:
            print(f'Player {current_player.name} rolls a {roll_value}')
            logging.info(
                f'Player {current_player.name} rolls a {roll_value}'
            )
        if len(moves) > 0:

            selected_move = current_player.choose_move(
                self._game_state, moves
            )

            for move_component in selected_move:
                self._game_state.do(move_component)

            if self.verbose:
                logging.debug(f'Available moves: {moves}')
                logging.info(f'Selected move: {selected_move}')
                logging.debug(
                    'Game state post-move.'
                    f'Waiting areas: {self._game_state.waiting_areas_to_dict()}'
                    f'Main spaces: {self._game_state.main_spaces_to_list()}'
                    f'Home areas: {self._game_state.home_areas_to_dict()}'
                )

        elif self.verbose:
            print('No moves possible.')
            logging.info('No moves possible')

        if self._game_state.is_winner(current_player.name):
            self._winner = current_player.name

    def next_player(self):
        return next(self._player_cycle)

    def roll(self):
        return randint(1, self.number_of_dice_faces)

    def get_game_state(self):
        return self._game_state
