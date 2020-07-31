"""Clovek ne jezi se game board and plays"""
from math import floor

import attr

import numpy as np

from .consts import (
    EMPTY_VALUE, MINIMUM_SECTION_LENGTH, PIECES_PER_PLAYER
)


class Board:
    """
    Game board representation, consisting of waiting area, main board,
    and home base representation. The internal representation of the game
    board is implemented in Game.

    The board state is represented by the main board and
    home base, while the waiting area is used only to determine
    allowable moves, e.g. if player A's waiting area has count 0,
    then she may not move a new symbol onto the main board.
    """
    def __init__(self, section_length, player_symbols=('1', '2', '3', '4')):
        self.section_length = section_length
        self.player_symbols = player_symbols

    def initialize(self):
        self.setup_spaces()
        self.setup_homes()
        self.setup_waiting_count()

    def setup_spaces(self):

        if self.section_length < MINIMUM_SECTION_LENGTH:
            raise ValueError(
                f'Sections must have length {MINIMUM_SECTION_LENGTH}'
                ' or greater'
            )

        if self.section_length % 2 != 0:
            raise ValueError('Sections must have even length')

        self.spaces = (
            len(self.player_symbols) * self.section_length * [EMPTY_VALUE]
        )

    def setup_homes(self):
        """Each player's home base consisting of 4 spots"""
        res = {}
        for symbol in self.player_symbols:
            res[symbol] = PIECES_PER_PLAYER * [EMPTY_VALUE]

        self.homes = res

    def setup_waiting_count(self):
        res = {}
        for symbol in self.player_symbols:
            res[symbol] = PIECES_PER_PLAYER

        self.waiting_count = res

    def _get_private_symbol(self, public_symbol):

        return self.player_symbols.index(public_symbol)

    def _get_public_symbol(self, private_symbol):
        return self.player_symbols[private_symbol]

    def __repr__(self):
        """Show board and players"""
        if self.section_length == 4:
            res = (
                "\n"
                "    -------------\n"
                "    | {6} | {7} | {8} |\n"
                "----------------------\n"
                "| {4} | {5} |    | {9} | {10} |\n"
                "--------      -------|\n"
                "| {3} |            | {11} |\n"
                "--------      -------|\n"
                "| {2} | {1} |    | {13} | {12} |\n"
                "----------------------\n"
                "    | {0} | {15} | {14} |\n"
                "    -------------"
            ).format(*self.spaces)

            for symbol in self.player_symbols:
                res += (
                    "\nplayer {} home: {} | {} | {} | {} "
                    .format(symbol, *(4 * [EMPTY_VALUE]))
                )
            return res

        else:
            raise NotImplementedError(
                'Board representation only for 16 space main board'
            )


@attr.s
class Game:

    players = attr.ib()
    section_length = attr.ib(default=4)

    def initialize(self):
        self.initialize_players()
        self.initialize_board()

    def initialize_players(self):
        self.n_players = len(self.players)
        self._validate_n_players()
        self._set_player_symbols()
        self._set_player_start()
        self._set_player_prehome()

    def _validate_n_players(self):

        all_n_players = [player.number_of_players for player in self.players]

        if not len(set(all_n_players)) == 1:
            raise ValueError('Differing number of players entered')

        if not self.n_players == self.players[0].number_of_players:
            raise ValueError(
                f'{len(self.players)} players entered, '
                f'but should be {self.n_players}'
            )

    def _set_player_symbols(self):
        """Set player orders, symbols and interface"""
        symbols = []
        for idx, player in enumerate(self.players):
            player.set_order(idx)
            symbols.append(player.symbol)

        if len(set(symbols)) < self.n_players:
            raise ValueError('Player symbols must be unique')

        self.player_symbols = symbols

    def _set_player_start(self):
        for idx, player in enumerate(self.players):
            player.set_start_position(idx, self.section_length)

    def _set_player_prehome(self):
        for idx, player in enumerate(self.players):
            player.set_prehome_position(idx, self.section_length)

    def is_winner(self, symbol):
        return self.board.homes[symbol] == PIECES_PER_PLAYER * [symbol]

    def initialize_board(self):
        self.board = Board(self.section_length, self.player_symbols)
        self.board.initialize()
        # Initialize array representations
        self.initialize_waiting_count_array()
        self.initialize_spaces_array()
        self.initialize_homes_array()

    def get_player(self, symbol):
        idx = np.argmax(np.array(self.player_symbols) == symbol)
        return self.players[idx]

    def initialize_waiting_count_array(self):
        res = [
            self.board.waiting_count.get(symbol)
            for symbol in self.player_symbols
        ]
        self._waiting_count = res

    def get_waiting_count_array(self):
        return self._waiting_count

    def set_waiting_count_array(self, symbol, count):
        private_symbol = self._to_private_symbol(symbol)
        self._waiting_count[private_symbol] = count

    def initialize_spaces_array(self):
        res = [self._to_private_symbol(symbol) for symbol in self.board.spaces]
        self._spaces_array = np.array(res)

    def get_spaces_array(self):
        return self._spaces_array

    def set_space_array(self, symbol, position):
        private_symbol = self._to_private_symbol(symbol)
        self._spaces_array[position] = private_symbol

    def initialize_homes_array(self):
        res = []
        for symbol in self.player_symbols:
            res.append([
                self._to_private_symbol(symbol)
                for symbol in self.board.homes.get(symbol)
            ])

        self._homes_array = res

    def get_homes_array(self):
        return self._homes_array

    def _to_private_symbol(self, symbol):
        if symbol == EMPTY_VALUE:
            return -1
        else:
            return self.player_symbols.index(symbol)

    def assign_to_space(self, symbol, idx):
        self._spaces_array[idx] = self._to_private_symbol(symbol)

    def leave_home_is_valid(self, symbol, roll):
        private_symbol = self._to_private_symbol(symbol)
        res = []

        # Check if a 6 rolled
        res.append(roll == 6)

        # Check if still symbol pieces in waiting area
        if self._waiting_count[private_symbol] > 0:
            res.append(True)
        else:
            res.append(False)

        # Check if symbol's start position is occupied
        start_position = self.get_player(symbol).get_start_position()
        res.append(self._spaces_array[start_position] == -1)

        return np.all(np.array(res))

    def is_space_advance(self, symbol, position, roll):
        """
        Determine if advance move is still among spaces, i.e.
        not in the symbol's home area
        """
        start = self.get_player(symbol).get_start_position()
        zeroed_position = position - start
        advance_after_prehome = floor(
            (zeroed_position + roll) / float(len(self._spaces_array))
        )
        res = not bool(advance_after_prehome)

        return res
