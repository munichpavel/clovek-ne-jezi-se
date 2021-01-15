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
        if current_player.print_to_screen:
            print(f'Player {current_player.name} rolls a {roll_value}')
        logging.info(
            f'Player {current_player.name} rolls a {roll_value}'
        )
        logging.debug(f'Available moves: {moves}')

        if len(moves) > 0:

            selected_move = current_player.choose_move(
                self._game_state, moves
            )

            for move_component in selected_move:
                self._game_state.do(move_component)
                logging.debug(f'\nDo move {move_component}')

            logging.debug(
                'Game state post-move.'
                f'\nWaiting areas: {self._game_state.waiting_areas_to_dict()}'
                f'\nMain spaces: {self._game_state.main_spaces_to_list()}'
                f'\nHome areas: {self._game_state.home_areas_to_dict()}'
            )
            if (
                getattr(current_player, 'draw', None) is not None
                and current_player.print_to_screen
            ):

                current_player.draw(self._game_state)

        else:
            if current_player.print_to_screen:
                print('No moves possible.\n')
            logging.info('No moves possible')

        counts = self._get_game_state_counts()
        logging.debug(f'\nBoard counts: {counts}')

        if self._game_state.is_winner(current_player.name):
            self._winner = current_player.name
            logging.info(f'Winner is {self._winner}')

    def _get_game_state_counts(self):
        """Convenience function for debugging.
        TODO refactor if really used by agents.
        """
        counts = {}
        waiting_list_list = list(
            self._game_state.waiting_areas_to_dict().values()
        )
        main_list = self._game_state.main_spaces_to_list()
        home_list_list = list(self._game_state.home_areas_to_dict().values())

        waiting_list = []
        home_list = []
        for sublist in waiting_list_list:
            for elt in sublist:
                waiting_list.append(elt)
        for sublist in home_list_list:
            for elt in sublist:
                home_list.append(elt)

        for player_name in self._player_names:
            piece_count = 0
            for space_list in [waiting_list, main_list, home_list]:
                for occupier in space_list:
                    if occupier == player_name:
                        piece_count += 1
            counts[player_name] = piece_count

        return counts

    def next_player(self):
        return next(self._player_cycle)

    def roll(self):
        return randint(1, self.number_of_dice_faces)

    def get_game_state(self):
        return self._game_state
