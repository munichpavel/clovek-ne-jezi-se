"""Tests for `clovek_ne_jezi_se` package."""

import pytest

from clovek_ne_jezi_se.consts import EMPTY_VALUE
from clovek_ne_jezi_se.game import Board, Game
from clovek_ne_jezi_se.agent import (
   Player, Players,
   FurthestAlongAgent
)


def monkey_roll(roll_value):
    return roll_value

class TestPlayer:
    player = Player('1')



    def test_repr(self):
        assert repr(self.player) == 'Player game piece 1'


    def test_home(self):
        assert len(self.player.home) == 4


    with pytest.raises(ValueError):
        player = Player(1)


    def test_dice_roll_monkeypatch(self, monkeypatch):

        monkeypatch.setattr(self.player, 'roll', lambda: monkey_roll(1))
        assert self.player._roll_is_valid(self.player.roll())

        monkeypatch.setattr(self.player, 'roll', lambda: monkey_roll(0))
        assert ~self.player._roll_is_valid(self.player.roll())

    def test_action_is_valid(self):

        assert self.player._action_is_valid([EMPTY_VALUE], 0)
        assert ~self.player._action_is_valid([EMPTY_VALUE], 1)


class TestFurthestAlongPlayer:
    symbol = '1'
    player = FurthestAlongAgent(symbol)

    def test_furthest_along_position(self):
        assert self.player._find_furthest_along_position(['1', '-', '1', '1']) == 3
        with pytest.raises(ValueError):
            self.player._find_furthest_along_position(['-'])


    

    def test_take_action(self, monkeypatch):
        monkeypatch.setattr(self.player, 'roll', lambda: monkey_roll(1))

        board = Board(4)
        assert self.player.take_action(board) == {}

        # Put one position in first home spot
        board.homes[self.symbol][0] = self.symbol
        assert self.player.take_action(board) == {'home': (0, 1)}

        board = Board(4)
        # Set game to non-initial state with two pieces on board
        board.spaces[0] = self.symbol
        board.spaces[2] = self.symbol
        
        assert self.player.take_action(board) == {'main': (2, 3)}

        
        assert self.player.take_action(board) == {'main': (2, 3)}


@pytest.fixture
def symbols():
    return ['1', '2', '3', '4']

@pytest.fixture
def players_input(symbols):
    return [Player(symbol=symbol) for symbol in symbols]

@pytest.fixture
def players(players_input):
    return Players(players_input)

class TestPlayers:
    
    with pytest.raises(ValueError):
        players = Players([
            Player(symbol='1'),
            Player(symbol='1'),
            Player(symbol='2'),
            Player(symbol='3'),
        ])
    

    def test_symbols(self, players, symbols):
       assert players.symbols == symbols

    def test_orders(self, players):
        for idx, symbol in enumerate(players.symbols):
            assert players.players[symbol].order == idx



@pytest.fixture
def small_initial_board():
    return Board(4)


@pytest.fixture
def expected_small_initial_board(small_initial_board):

    symbols = ['1', '2', '3', '4']
    '''Stub test, for refactoring of board representation'''

    res = ("\n" \
        "    -------------\n" \
        "    | {6} | {7} | {8} |\n" \
        "----------------------\n" \
        "| {4} | {5} |    | {9} | {10} |\n"    \
        "--------      -------|\n" \
        "| {3} |            | {11} |\n"    \
        "--------      -------|\n" \
        "| {2} | {1} |    | {12} | {13} |\n"    \
        "----------------------\n" \
        "    | {0} | {15} | {14} |\n" \
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
            assert small_initial_board.homes[symbol] == 4 * [EMPTY_VALUE]
    

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
            game.board.homes[symbol] = 4 * [symbol]
            assert game.is_winner(symbol)

    def test_player_start_position(self, players):
        # Mini board
        Game(players, 4)
        players.players['1']._start_position == 0
        players.players['2']._start_position == 4
        players.players['3']._start_position == 8
        players.players['4']._start_position == 12

        # Normal board
        Game(players, 10)
        players.players['1']._start_position == 0
        players.players['2']._start_position == 10
        players.players['3']._start_position == 20
        players.players['4']._start_position == 30

