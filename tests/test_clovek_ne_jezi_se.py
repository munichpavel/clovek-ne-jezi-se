"""Tests for `clovek_ne_jezi_se` package."""

import pytest

from clovek_ne_jezi_se.game import Board, Player, Players


class TestPlayer:
    player = Player(None, '1')

    assert repr(player) == 'Player agent None, game piece 1'

@pytest.fixture
def players_input():
    return [
        Player(None, symbol='1'),
        Player(None, symbol='2'),
        Player(None, symbol='3'),
        Player(None, symbol='4'),
    ]

class TestPlayers:
    
    with pytest.raises(ValueError):
        players = Players([
            Player(None, symbol='1'),
            Player(None, symbol='1'),
            Player(None, symbol='2'),
            Player(None, symbol='3'),
        ])

    def test_symbols(self, players_input):
        players = Players(players_input)

        assert players.symbols == ['1', '2', '3', '4']
    


@pytest.fixture
def empty_value():
    return '-'

@pytest.fixture
def small_board(empty_value):
    return Board(4, empty_value=empty_value)


@pytest.fixture
def expected_empty_board_small(small_board, empty_value):
    '''Stub test, for refactoring of board representation'''
    return ( "\n" \
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
    ).format(*(16 * (empty_value)))

class TestBoard:

    def test_board_setup(self):
        board = Board(10)
        assert len(board.spaces) == 4 * 10

        # Board cannot have too short sections
        with pytest.raises(ValueError):
            board = Board(3)
        
        # Board cannot have odd section lengths
        with pytest.raises(ValueError):
            board = Board(5)
    

    def test_board_representation(
        self, small_board, 
        expected_empty_board_small
    ):

        assert repr(small_board) == expected_empty_board_small
        

