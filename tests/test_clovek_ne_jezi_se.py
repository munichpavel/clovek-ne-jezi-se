"""Tests for `clovek_ne_jezi_se` package."""

import pytest

from clovek_ne_jezi_se.game import Board, Game

from clovek_ne_jezi_se.agent import (
    EMPTY_VALUE, Player, Players,
)


class TestPlayer:
    player = Player(None, '1')
    
    def test_repr(self):
        assert repr(self.player) == 'Player agent None, game piece 1'


    def test_home(self):
        assert len(self.player.home) == 4


    with pytest.raises(ValueError):
        player = Player(None, 1)


    def test_dice_roll_monkeypatch(self, monkeypatch):

        def monkey_roll(roll_value):
            return roll_value

        monkeypatch.setattr(self.player, 'roll', lambda: monkey_roll(1))
        assert self.player._roll_is_valid(self.player.roll())

        monkeypatch.setattr(self.player, 'roll', lambda: monkey_roll(0))
        assert ~self.player._roll_is_valid(self.player.roll())



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
def small_initial_board():
    return Board(4)


@pytest.fixture
def expected_small_initial_board(small_initial_board):

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

    def test_homes_setup(self, small_initial_board):

        for symbol in ('1', '2', '3', '4'):
            assert small_initial_board.homes[symbol] == 4 * (EMPTY_VALUE)
    

    def test_board_representation(
        self, small_initial_board, 
        expected_small_initial_board
    ):

        assert repr(small_initial_board) == expected_small_initial_board

    def test_player_representation(self, small_initial_board, symbols):

        for i in range(len(symbols)):
            assert small_initial_board._get_private_symbol(symbols[i]) == i
            assert small_initial_board._get_public_symbol(i) == symbols[i]


class TestGame:

    def test_game_setup(self, players, symbols):
        game = Game(players)

        assert len(game.board.spaces) == 4 * 4
        for symbol in symbols:
            assert len(game.board.homes[symbol]) == 4
            assert game.board.waiting_count[symbol] == 4


    def test_wins(self, players, symbols):
        # No winner for initialized board
        game = Game(players)
        assert game._winner == -1

        
        for symbol in players.symbols:
            # No winners with initial board
            assert ~game.is_winner(symbol)
             # Fill each player's home base to winning
            game.board.homes[symbol] = 4 * (symbol)
            assert game.is_winner(symbol)