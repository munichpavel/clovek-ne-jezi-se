"""Clovek ne jezi se game board and plays"""
import attr

from .consts import EMPTY_VALUE, PIECES_PER_PLAYER


class Board:
    """
    Game goard, consisting of waiting area, main board,
    and home base representation.

    The board state is represented by the main board and
    home base, while the waiting area is used only to determine
    allowable moves, e.g. if player A's waiting area has count 0,
    then she may not move a new symbol onto the main board.
    """
    def __init__(self, section_length, symbols=('1', '2', '3', '4')):
        self.section_length = section_length
        self.spaces = self._setup_spaces(EMPTY_VALUE)
        self.symbols = symbols
        self.homes = self._setup_homes()
        self.waiting_count = self._setup_waiting()

    def _setup_spaces(self, EMPTY_VALUE):

        if self.section_length < 4:
            raise ValueError('Sections must have length 4 or greater')

        if self.section_length % 2 != 0:
            raise ValueError('Sections must have even length')

        return 4 * self.section_length * [EMPTY_VALUE]

    def _setup_homes(self):
        """Each player's home base consisting of 4 spots"""
        res = {}
        for symbol in self.symbols:
            res[symbol] = 4 * [EMPTY_VALUE]

        return res

    def _setup_waiting(self):
        res = {}
        for symbol in self.symbols:
            res[symbol] = 4

        return res

    def _get_private_symbol(self, public_symbol):

        return self.symbols.index(public_symbol)

    def _get_public_symbol(self, private_symbol):
        return self.symbols[private_symbol]

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

            for symbol in self.symbols:
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
        self._set_player_start()
        self._set_player_prehome()

    def _set_player_start(self):
        for idx, player in enumerate(self.players.players.values()):
            player.set_start_position(idx, self.section_length)

    def _set_player_prehome(self):
        for idx, player in enumerate(self.players.players.values()):
            player.set_prehome_position(idx, self.section_length)

    def is_winner(self, symbol):
        return self.board.homes[symbol] == PIECES_PER_PLAYER * [symbol]

    def initialize_board(self):
        self.board = Board(self.section_length, self.players.symbols)
