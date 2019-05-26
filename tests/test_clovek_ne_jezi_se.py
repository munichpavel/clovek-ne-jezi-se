"""Tests for `clovek_ne_jezi_se` package."""

import pytest

from clovek_ne_jezi_se.game import (
    EMPTY_VALUE,
    Board, Player, Players
)


class TestPlayer:
    player = Player(None, '1')
    
    def test_repr(self):
        assert repr(self.player) == 'Player agent None, game piece 1'

    def test_home(self):
        assert len(self.player.home) == 4


@pytest.fixture
def symbols():
    return ['1', '2', '3', '4']

@pytest.fixture
def players_input(symbols):
    return [Player(None, symbol=symbol) for symbol in symbols]

@pytest.fixture
def players(players_input):
    return Players(players_input)

class TestPlayers:
    
    with pytest.raises(ValueError):
        players = Players([
            Player(None, symbol='1'),
            Player(None, symbol='1'),
            Player(None, symbol='2'),
            Player(None, symbol='3'),
        ])

    
    def test_symbols(self, players, symbols):

        assert players.symbols == symbols
    


@pytest.fixture
def small_empty_board():
    return Board(4)


@pytest.fixture
def expected_empty_board_small(small_empty_board):

    symbols = ['1', '2', '3', '4']
    '''Stub test, for refactoring of board representation'''

    res = ("\n" \
        "    -------------\n" \
        "    | {0} | {1} | {2} |\n" \
        "----------------------\n" \
        "| {14} | {15} |    | {3} | {4} |\n"    \
        "--------      -------|\n" \
        "| {13} |            | {5} |\n"    \
        "--------      -------|\n" \
        "| {12} | {11} |    | {7} | {6} |\n"    \
        "----------------------\n" \
        "    | {10} | {9} | {8} |\n" \
        "    -------------"
    ).format(*(16 * (EMPTY_VALUE)))

    for symbol in symbols:
        res +=  (
        "\nplayer {} home: {} | {} | {} | {} "
        .format(symbol, * (4 * (EMPTY_VALUE)))
    )
    return res



class TestBoard:

    def test_spaces_setup(self):
        board = Board(10)
        assert len(board.spaces) == 4 * 10

        # Board cannot have too short sections
        with pytest.raises(ValueError):
            board = Board(3)
        
        # Board cannot have odd section lengths
        with pytest.raises(ValueError):
            board = Board(5)

    def test_homes_setup(self):
        board = Board(4)

        for symbol in ('1', '2', '3', '4'):
            assert board.homes[symbol] == 4 * (EMPTY_VALUE)
    

    def test_board_representation(
        self, small_empty_board, 
        expected_empty_board_small
    ):

        assert repr(small_empty_board) == expected_empty_board_small
