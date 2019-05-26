"""Tests for `clovek_ne_jezi_se` package."""

import pytest

from clovek_ne_jezi_se.game import Board

class TestGame:

    def test_board_setup(self):
        board = Board(10)
        assert len(board.spaces) == 4 * 10

        # Board cannot have too short sections
        with pytest.raises(ValueError):
            board = Board(3)
        
        # Board cannot have odd section lengths
        with pytest.raises(ValueError):
            board = Board(5)


        

