"""Tests for `clovek_ne_jezi_se` package."""
from copy import deepcopy
import pytest

import numpy as np

from clovek_ne_jezi_se.consts import EMPTY_VALUE
from clovek_ne_jezi_se.game import Board, Game
from clovek_ne_jezi_se.agent import Player


def monkey_roll(roll_value):
    return roll_value


class TestPlayer:
    player = Player('1', number_of_players=4)
    player.initialize_home()

    def test_home(self):
        assert len(self.player.home) == 4

    with pytest.raises(TypeError):
        Player(1, number_of_players=4)

    def test_dice_roll_monkeypatch(self, monkeypatch):

        monkeypatch.setattr(self.player, 'roll', lambda: monkey_roll(1))
        assert self.player.roll_is_valid(self.player.roll())

        monkeypatch.setattr(self.player, 'roll', lambda: monkey_roll(0))
        assert ~self.player.roll_is_valid(self.player.roll())


@pytest.fixture
def small_initial_board():
    board = Board(4)
    board.initialize()
    return board


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
        board.initialize()

        assert len(board.spaces) == 4 * 10

        # Board cannot have too short sections
        with pytest.raises(ValueError):
            board = Board(3)
            board.initialize()

        # Board cannot have odd section lengths
        with pytest.raises(ValueError):
            board = Board(5)
            board.initialize()

    def test_homes_setup(self, small_initial_board):

        for symbol in ('1', '2', '3', '4'):
            assert small_initial_board.homes[symbol] == 4 * [EMPTY_VALUE]

    def test_board_representation(
        self, small_initial_board,
        expected_small_initial_board
    ):

        assert repr(small_initial_board) == expected_small_initial_board

    def test_player_representation(self, small_initial_board):

        for i, symbol in enumerate(['1', '2', '3', '4']):
            assert small_initial_board._get_private_symbol(symbol) == i
            assert small_initial_board._get_public_symbol(i) == symbol


@pytest.fixture
def players():
    res = []
    for symbol in ['1', '2', '3', '4']:
        player = Player(symbol=symbol, number_of_players=4)
        player.initialize_home()
        res.append(player)
    return res


class TestGame:
    players = []
    for symbol in ['1', '2', '3', '4']:
        player = Player(symbol=symbol, number_of_players=4)
        player.initialize_home()
        players.append(player)

    mini_game = Game(players, section_length=4)
    mini_game.initialize()

    full_game = Game(deepcopy(players), section_length=10)
    full_game.initialize()

    def test_game_setup(self):

        assert len(self.mini_game.board.spaces) == self.mini_game.n_players * 4
        for symbol in ['1', '2', '3', '4']:
            assert len(self.mini_game.board.homes[symbol]) == 4
            assert self.mini_game.board.waiting_count[symbol] == 4

    def test_initializtion_errors(self):
        with pytest.raises(ValueError):
            wonky_symbols_game = Game([
                Player(symbol='1', number_of_players=4),
                Player(symbol='1', number_of_players=4),
                Player(symbol='2', number_of_players=4),
                Player(symbol='3', number_of_players=4),
            ])
            wonky_symbols_game.initialize_players()

        with pytest.raises(ValueError):
            inconsistent_n_player_game = Game([
                Player(symbol='0', number_of_players=2),
                Player(symbol='1', number_of_players=3),
            ])
            inconsistent_n_player_game.initialize_players()

        with pytest.raises(ValueError):
            wrong_n_players_game = Game([
                Player(symbol='0', number_of_players=1),
                Player(symbol='1', number_of_players=1),
            ])
            wrong_n_players_game.initialize_players()

    def test_wins(self):
        # No winner for initialized board
        for symbol in self.mini_game.player_symbols:
            # No winners with initial board
            assert ~self.mini_game.is_winner(symbol)
            # Fill each player's home base to winning
            self.mini_game.board.homes[symbol] = 4 * [symbol]
            assert self.mini_game.is_winner(symbol)

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
        self, symbol, expected_position
    ):
        # Mini board
        assert (
            self.mini_game.get_player(symbol).get_start_position()
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
        self, symbol, expected_position
    ):
        # Normal board
        assert (
            self.full_game.get_player(symbol).get_start_position()
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
    def test_player_mini_pre_home_position(self, symbol, position):
        assert (
            self.mini_game
            .get_player(symbol)
            .get_prehome_position() == position
        )

    @pytest.mark.parametrize(
        'symbol,position',
        [
            ('1', 39),
            ('2', 9),
            ('3', 19),
            ('4', 29)
        ])
    def test_player_normal_pre_home_position(self, symbol, position):
        assert (
            self.full_game.get_player(symbol).get_prehome_position()
            == position
        )

    def test_get_initial_arrays(self):
        # Test get array methods for initialized game
        # Waiting count array
        np.testing.assert_array_equal(
            self.mini_game.get_waiting_count_array(),
            np.array(4 * [4])
        )

        # Spaces
        np.testing.assert_array_equal(
            self.mini_game.get_spaces_array(),
            -1 * np.ones(len(self.mini_game.board.spaces))
        )

        # Homes
        np.testing.assert_array_equal(
            self.mini_game.get_homes_array(),
            -1 * np.ones((4, self.mini_game.n_players))
        )

    @pytest.mark.parametrize(
        'symbol_idx,space_idx',
        [(0, 0), (1, 0), (3, 1)]
    )
    def test_assignments(self, symbol_idx, space_idx):
        symbol = self.mini_game.player_symbols[symbol_idx]
        self.mini_game.assign_to_space(symbol, space_idx)

        # Define expected array by modifying spaces array
        expected = self.mini_game.get_spaces_array()
        expected[space_idx] = symbol_idx

        np.testing.assert_array_equal(
            self.mini_game.get_spaces_array(),
            expected
        )


class TestGameAction:

    symbols = ['1', '2', '3', '4']
    players = []
    for symbol in symbols:
        player = Player(symbol=symbol, number_of_players=4)
        player.initialize_home()
        players.append(player)

    game = Game(players, section_length=4)
    game.initialize()

    # Empty waiting area of one symbol for an invalid move
    game.set_waiting_count_array('2', count=0)

    # Occupy one start position for an invalid move
    game.set_space_array('1', game.get_player('3').get_start_position())

    def test_leave_home_is_valid(self):

        for symbol in ['1', '4']:
            assert self.game.leave_home_is_valid(symbol=symbol, roll=6)
            # Any other roll is invalid to leave home
            for roll in range(1, 6):
                assert not (
                    self.game.leave_home_is_valid(symbol=symbol, roll=roll)
                )

    @pytest.mark.parametrize(
        'symbol,position,roll,expected',
        [
            ('1', 0, 3, True),
            ('2', 0, 3, False),
            ('1', 14, 1, True),
            ('1', 15, 1, False)
        ]
    )
    def test_is_space_advance(self, symbol, position, roll, expected):
        assert (
            self.game.is_space_advance(
                symbol=symbol, position=position, roll=roll
            ) == expected
        )
