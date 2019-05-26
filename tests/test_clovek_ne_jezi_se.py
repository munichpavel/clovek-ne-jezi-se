"""Tests for `clovek_ne_jezi_se` package."""

import pytest

from clovek_ne_jezi_se.game import Board, BoardValues

@pytest.fixture
def empty_board_small():
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
    ).format(*(16 * [BoardValues.EMPTY.value]))

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
    
    def test_board_representation(self, empty_board_small):
        # Test board representation
        board = Board(4)
        assert repr(board) == empty_board_small

        

