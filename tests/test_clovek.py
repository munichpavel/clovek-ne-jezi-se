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
    player = Player('1', number_of_players=4)

    def test_repr(self):
        assert repr(self.player) == 'Player game piece 1'

    def test_home(self):
        assert len(self.player.home) == 4

    with pytest.raises(ValueError):
        player = Player(1, number_of_players=4)

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
    player = FurthestAlongAgent(symbol, number_of_players=4)

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


@pytest.fixture
def symbols():
    return ['1', '2', '3', '4']

@pytest.fixture
def players_input(symbols):
    return [Player(symbol=symbol, number_of_players=4) for symbol in symbols]

@pytest.fixture
def players(players_input):
    return Players(players_input)


class TestPlayers:

    with pytest.raises(ValueError):
        Players([
            Player(symbol='1', number_of_players=4),
            Player(symbol='1', number_of_players=4),
            Player(symbol='2', number_of_players=4),
            Player(symbol='3', number_of_players=4),
        ])

    with pytest.raises(ValueError):
        Players([
            Player(symbol='0', number_of_players=2),
            Player(symbol='1', number_of_players=3),
        ])

    with pytest.raises(ValueError):
        Players([
            Player(symbol='0', number_of_players=1),
            Player(symbol='1', number_of_players=1),
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
    """Stub test, for refactoring of board representation"""

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
    ).format(*(16 * (EMPTY_VALUE)))

    for symbol in symbols:
        res += (
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
        game.initialize()

        assert len(game.board.spaces) == game.players.n_players * 4
        for symbol in symbols:
            assert len(game.board.homes[symbol]) == 4
            assert game.board.waiting_count[symbol] == 4

    def test_wins(self, players, symbols):
        # No winner for initialized board
        game = Game(players)
        game.initialize()

        for symbol in players.symbols:
            # No winners with initial board
            assert ~game.is_winner(symbol)
            # Fill each player's home base to winning
            game.board.homes[symbol] = 4 * [symbol]
            assert game.is_winner(symbol)

    @pytest.mark.parametrize(
        'symbol,expected_position',
        [
            ('1', 0),
            ('2', 4),
            ('3', 8),
            ('4', 12)
        ]
    )
    def test_player_mini_start_position(
        self, players, symbol, expected_position
    ):
        # Mini board
        game = Game(players, section_length=4)
        game.initialize()

        assert (
            game.players.players[symbol].get_start_position()
            == expected_position
        )

    @pytest.mark.parametrize(
        'symbol,expected_position',
        [
            ('1', 0),
            ('2', 10),
            ('3', 20),
            ('4', 30)
        ]
    )
    def test_player_normal_start_position(
        self, players, symbol, expected_position
    ):
        # Normal board
        game = Game(players, section_length=10)
        game.initialize()

        assert (
            game.players.players[symbol].get_start_position()
            == expected_position
        )

    @pytest.mark.parametrize(
        'symbol,position',
        [
            ('1', 15),
            ('2', 3),
            ('3', 7),
            ('4', 11)
        ])
    def test_player_mini_pre_home_position(self, players, symbol, position):
        # Mini board
        game = Game(players, section_length=4)
        game.initialize()

        assert game.players.players[symbol].get_prehome_position() == position

    @pytest.mark.parametrize(
        'symbol,position',
        [
            ('1', 39),
            ('2', 9),
            ('3', 19),
            ('4', 29)
        ])
    def test_player_normal_pre_home_position(self, players, symbol, position):
        # Mini board
        game = Game(players, section_length=10)
        game.initialize()

        assert game.players.players[symbol].get_prehome_position() == position
