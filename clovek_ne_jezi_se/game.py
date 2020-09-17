"""Clovek ne jezi se game board and plays"""
from math import floor

import attr

import numpy as np

from .consts import (
    EMPTY_VALUE, MINIMUM_SECTION_LENGTH, PIECES_PER_PLAYER, NR_OF_DICE_FACES,
    MOVE_KINDS
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

    def get_private_symbol(self, public_symbol):

        return self.player_symbols.index(public_symbol)

    def get_public_symbol(self, private_symbol):
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
                    "\nplayer {} pieces in waiting area: {} "
                    .format(symbol, self.waiting_count[symbol])
                )
                res += (
                    "\nplayer {} home: {} | {} | {} | {}\n"
                    .format(symbol, *(self.homes[symbol]))
                )
            return res

        else:
            raise NotImplementedError(
                'Board representation only for 16 space main board'
            )


def check_start(self, attribute, value):
    # TODO: Refactor as in exapmple
    # https://www.attrs.org/en/stable/api.html#attr.validators.in_
    if value is not None and self.kind == 'leave_waiting':
        raise ValueError(
            'Leave home moves may not have a start position'
        )


@attr.s
class Move:
    """
    Container for game moves based on array (internal) board representation.
    """
    symbol = attr.ib()
    kinds = MOVE_KINDS
    kind = attr.ib()
    roll = attr.ib(kw_only=True)
    start = attr.ib(kw_only=True, default=None, validator=check_start)
#    end = attr.ib(kw_only=True, default=None)

    @kind.validator
    def check_kind(self, attribute, value):
        if value not in self.kinds:
            raise ValueError(f'Move kind must be a member of {self.kinds}')


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
            player.set_start(idx, self.section_length)

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

    # Board methods
    def initialize_waiting_count_array(self):
        res = [
            self.board.waiting_count.get(symbol)
            for symbol in self.player_symbols
        ]
        self._waiting_count = np.array(res)

    def get_waiting_count_array(self):
        return self._waiting_count

    def set_waiting_count_array(self, symbol, count):
        self.board.waiting_count[symbol] = count

        private_symbol = self._to_private_symbol(symbol)
        self._waiting_count[private_symbol] = count

    def initialize_spaces_array(self):
        res = [self._to_private_symbol(symbol) for symbol in self.board.spaces]
        self._spaces_array = np.array(res)

    def get_spaces_array(self):
        return self._spaces_array

    def set_space_array(self, symbol, position):
        self.board.spaces[position] = symbol

        private_symbol = self._to_private_symbol(symbol)
        self._spaces_array[position] = private_symbol

    def initialize_homes_array(self):
        res = []
        for symbol in self.player_symbols:
            res.append([
                self._to_private_symbol(symbol)
                for symbol in self.board.homes.get(symbol)
            ])

        self._homes_array = np.array(res)

    def get_homes_array(self):
        return self._homes_array

    def set_homes_array(self, symbol, position):
        self.board.homes[symbol][position] = symbol

        private_symbol = self._to_private_symbol(symbol)
        self._homes_array[private_symbol, position] = private_symbol

    def _to_private_symbol(self, symbol):
        if symbol == EMPTY_VALUE:
            return -1
        else:
            return self.player_symbols.index(symbol)

    def assign_to_space(self, symbol, idx):
        """Convenience function. TODO: Deprecate or make private?"""
        self._spaces_array[idx] = self._to_private_symbol(symbol)

    # Moves
    def get_all_moves(self, symbol, roll):
        res = {}
        for kind in MOVE_KINDS:
            res[kind] = self.get_moves_of(symbol, kind, roll)

        return res

    def get_moves_of(self, symbol, kind, roll):
        res = []
        starts = self.get_move_starts(symbol, kind)
        for start in starts:
            try:
                move = self.move_factory(symbol, kind, roll, start)
                res.append(move)
            except ValueError:
                continue

        return res

    def get_move_starts(self, symbol, kind):
        """
        Get potential starting positions for symbol and move kind.
        No validation is performed.
        """
        if kind == 'leave_waiting':
            return self._get_leave_waiting_starts(symbol)
        elif kind == 'space_advance':
            return self._get_space_advance_starts(symbol)
        elif kind == 'space_to_home':
            return self._get_space_to_home_starts(symbol)
        else:  # home_advance
            return self._get_home_advance_starts(symbol)

    def _get_leave_waiting_starts(self, symbol):
        return [None]

    def _get_space_advance_starts(self, symbol):
        return self.get_symbol_space_positions(symbol)

    def _get_space_to_home_starts(self, symbol):
        return self.get_symbol_space_positions(symbol)

    def _get_home_advance_starts(self, symbol):
        return self.get_symbol_home_positions(symbol)

    def move_factory(self, symbol, kind, roll, start=None):
        move = self._get_move(symbol, kind, roll, start)
        is_valid = self._get_validator(kind)
        if is_valid(move):
            return move
        else:
            # TODO raise reasonable error--see #9.
            raise ValueError('Invalid move entered')

    def _get_move(self, symbol, move_kind, roll, start):
        if move_kind == 'leave_waiting':
            return Move(symbol, move_kind, roll=roll)
        else:
            return Move(
                symbol, move_kind, roll=roll, start=start
            )

    def _get_validator(self, move_kind):
        if move_kind == 'leave_waiting':
            return self.leave_waiting_validator
        elif move_kind == 'space_advance':
            return self.space_advance_validator
        elif move_kind == 'space_to_home':
            return self.space_to_home_validator
        else:  # home_advance
            return self.home_advance_validator

    def leave_waiting_validator(self, move):
        """
        Parameters
        ----------
        move : Move

        Returns
        -------
        res : Boolean
        """
        return self.leave_waiting_is_valid(move.symbol, move.roll)

    def leave_waiting_is_valid(self, symbol, roll):
        """
        Parameters
        ----------
        symbol : string
        roll : int

        Returns
        -------
         : Boolean
        """
        private_symbol = self._to_private_symbol(symbol)
        res = []

        # Check if a maximum rolled (usually 6)
        res.append(roll == NR_OF_DICE_FACES)

        # Check if still symbol pieces in waiting area
        if self._waiting_count[private_symbol] > 0:
            res.append(True)
        else:
            res.append(False)

        # Check if symbol's start position is occupied
        start = self.get_player(symbol).get_start()
        res.append(self._spaces_array[start] == -1)

        return np.all(np.array(res))

    # Space advance move methods
    def space_advance_validator(self, move):
        if not self.is_space_advance_move(move.symbol, move.roll, move.start):
            return False

        return self.space_advance_not_blocked(
            move.symbol, move.roll, move.start
        )

    def get_symbol_space_positions(self, symbol):
        """
        Parameters
        ----------
        symbol : string
            Must be one of player symbols

        Returns
        -------
        symbol_positions : numpy.array
            1-d array of game board space indices where symbol has pieces
        """
        private_symbol = self._to_private_symbol(symbol)
        spaces_array = self.get_spaces_array()
        symbol_positions = np.where(spaces_array == private_symbol)[0]

        return symbol_positions

    def is_space_advance_move(self, symbol, roll, start):
        """
        Determine if space advance move, sans validity checks.


        Parameters
        ----------
        symbol : string
        roll : int
        move_start : int

        Returns
        -------
         : Boolean
         """
        player_start = self.get_player(symbol).get_start()
        zeroed_position = (start - player_start) % len(self._spaces_array)

        advance_ratio_of_spaces = (
            (zeroed_position + roll) / float(len(self._spaces_array))
        )

        after_prehome_ratio_rounded = floor(advance_ratio_of_spaces)

        res = not bool(after_prehome_ratio_rounded)

        return res

    def space_advance_not_blocked(self, symbol, roll, start):
        """
        Note: Assumes advance (start + roll) remains among spaces,
        otherwise will throw an (index) error.
        """
        return self._spaces_array[roll + start] == -1

    # Space to home move methods
    def space_to_home_validator(self, move):
        # TODO Refactor to follow single-responsibility principle
        is_space_to_home = self.is_space_to_home_move(
            move.symbol, move.roll, move.start
        )
        is_valid = self.space_to_home_is_valid(
            move.symbol, move.roll, move.start
        )

        return is_space_to_home and is_valid

    def is_space_to_home_move(self, symbol, roll, start):
        """
        Determine if move is from (main) board space to home area,
        sans validity checks.

        Parameters
        ----------
        symbol : string
        position : int
        roll : int

        Returns
        -------
         : Boolean
        """
        return not self.is_space_advance_move(symbol, roll, start)

    def space_to_home_is_valid(self, symbol, roll, start):
        """
        TODO: Refactor to follow single-responsibility principle
        A home advance can be invalid in two ways:
          * the advance goes beyond the home spots
          * the advance position is occupied
        """
        res = []

        # Advance position not beyond last home spot, i.e. within home
        symbol_prehome = self.get_player(symbol).get_prehome_position()
        position_past_prehome = (
            (start + roll - symbol_prehome) % len(self._spaces_array)
        )
        within_home = position_past_prehome <= PIECES_PER_PLAYER
        res.append(within_home)

        # Advance position unoccupied
        if within_home:
            private_symbol = self._to_private_symbol(symbol)
            advance_position_unoccupied = (
                self._homes_array[private_symbol, position_past_prehome] == -1
            )
            res.append(advance_position_unoccupied)

        return np.all(np.array(res))

    # Home advance move methods
    def home_advance_validator(self, move):
        return self.home_advance_is_valid(move.symbol, move.roll, move.start)

    def home_advance_is_valid(self, symbol, roll, start):
        """
        A home advance is invalid if the end position is occupied
        or would land outside of the home spaces.

        Parameters
        ----------
        symbol : string
        roll : int
        start : int

        Returns
        -------
         : Boolean
        """
        end = start + roll

        if end > PIECES_PER_PLAYER - 1:
            return False

        symbol_home_positions = self.get_symbol_home_positions(symbol)

        return end not in symbol_home_positions

    def get_symbol_home_positions(self, symbol):
        """
        Parameters
        ----------
        symbol : string

        Returns
        -------
        symbol_positions : np.array
            Positions occupied by a symbol piece.
        """
        symbol_home_array = self.get_symbol_home_array(symbol)
        private_symbol = self._to_private_symbol(symbol)
        symbol_positions = np.where(symbol_home_array == private_symbol)[0]

        return symbol_positions

    def get_symbol_home_array(self, symbol):
        """
        Parameters
        ----------
        symbol : string

        Returns
        -------
         : np.array
            Symbol home array representation.
        """
        private_symbol = self._to_private_symbol(symbol)

        return self.get_homes_array()[private_symbol, :]

    # Do moves
    def do(self, move):
        # Check move validity
        # TODO: Do I need this? Duplication of factory?
        # Not if user can create own moves
        is_valid = self._get_validator(move.kind)
        if self._is_valid(move):
            print('yoyowassup')
        else:
            # TODO determine which error to raise
            raise ValueError
