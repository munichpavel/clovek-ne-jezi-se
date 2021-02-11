"""Client module for controlling game progression"""
import logging
from typing import Sequence, Tuple
from itertools import cycle
from random import randint

import attr

from clovek_ne_jezi_se.agents import Player
from clovek_ne_jezi_se.log_handler import handler
from clovek_ne_jezi_se.game_state import (
    EMPTY_SYMBOL, GameState
)

logger = logging.getLogger(__name__)
logger.addHandler(handler)


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
        self.winner = None
        self.play_count = 0

    def play(self) -> Tuple['Player', int]:
        """Play until a player wins wins"""

        while(self.winner is None):
            self.take_turn()
            self.play_count += 1

        return self.winner, self.play_count

    def take_turn(self):
        """Take a single player turn"""
        current_player = self.next_player()

        players_turn_continues = True
        while players_turn_continues:
            roll_value = self.roll()

            self.log(current_player, f'Rolls a {roll_value}')

            self._choose_and_do_move(current_player, roll_value)

            counts = self._get_game_state_counts()
            self.log(current_player, f'Board counts: {counts}')

            if self._game_state.is_winner(current_player.name):
                self.winner = current_player
                self.log(current_player, 'wins')

            players_turn_continues = (
                roll_value == self._game_state.number_of_dice_faces
            )

    def next_player(self):
        return next(self._player_cycle)

    def roll(self):
        return randint(1, self.number_of_dice_faces)

    def log(self, player, message):
        message = f'{player}:' + message
        logger.debug(message)

    def _choose_and_do_move(self, current_player, roll_value):
        moves = self._game_state.get_player_moves(
                roll_value, current_player.name
            )
        self.log(current_player, f'Available moves: {moves}')

        if len(moves) > 0:
            if (
                getattr(current_player, 'draw', None) is not None
                and current_player.print_game_state
            ):
                current_player.draw(self._game_state)
            selected_move = current_player.choose_move(
                self._game_state, moves
            )

            for move_component in selected_move:
                self._game_state.do(move_component)
                self.log(current_player, f'Do move {move_component}')

            self.log(
                current_player,
                'Game state post-move.'
                f'\nWaiting areas: {self._game_state.waiting_areas_to_dict()}'
                f'\nMain spaces: {self._game_state.main_spaces_to_list()}'
                f'\nHome areas: {self._game_state.home_areas_to_dict()}'
            )
        else:
            self.log(current_player, 'No moves possible')

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

    def get_game_state(self):
        return self._game_state
