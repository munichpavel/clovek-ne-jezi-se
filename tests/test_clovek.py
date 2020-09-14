"""Tests for `clovek_ne_jezi_se` package."""
from copy import deepcopy
import pytest

import numpy as np

from clovek_ne_jezi_se.consts import (
    EMPTY_VALUE, PIECES_PER_PLAYER, NR_OF_DICE_FACES
)
from clovek_ne_jezi_se.game import Board, Game, Move
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


class TestBoard:

    def test_spaces_setup(self):
        board = Board(10)
        board.initialize()

        assert len(board.spaces) == PIECES_PER_PLAYER * 10

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
            assert (
                small_initial_board.homes[symbol]
                == PIECES_PER_PLAYER * [EMPTY_VALUE]
            )

    def test_player_representation(self, small_initial_board):
        for symbol in ['1', '2', '3', '4']:
            assert small_initial_board.get_public_symbol(
                small_initial_board.get_private_symbol(symbol)
             ) == symbol


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
            assert len(self.mini_game.board.homes[symbol]) == PIECES_PER_PLAYER
            assert (
                self.mini_game.board.waiting_count[symbol] == PIECES_PER_PLAYER
            )

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
            self.mini_game.board.homes[symbol] = PIECES_PER_PLAYER * [symbol]
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

    @pytest.mark.parametrize(
        'method,expected',
        [
            ('get_waiting_count_array', np.array(4 * [PIECES_PER_PLAYER])),
            ('get_spaces_array', -1 * np.ones(len(mini_game.board.spaces))),
            (
                'get_homes_array',
                -1 * np.ones((PIECES_PER_PLAYER, mini_game.n_players))
            )
        ]
    )
    def test_get_initial_arrays(self, method, expected):
        # Test get array methods for initialized game
        game_array = getattr(self.mini_game, method)()
        assert isinstance(game_array, np.ndarray)
        np.testing.assert_array_equal(game_array, expected)

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


class TestMoves:
    def test_validators(self):

        with pytest.raises(TypeError):
            # start and end positions are keyword-required arguments
            Move('1', 'space_advance', 0, 2)

        with pytest.raises(ValueError):
            Move('1', 'nonsense_move', start=0, end=5)

        # Start position must be None for leave_home move
        with pytest.raises(ValueError):
            Move('1', 'leave_home', start=0)


class TestGameAction:
    symbols = ['1', '2', '3', '4']
    players = []
    for symbol in symbols:
        player = Player(symbol=symbol, number_of_players=4)
        player.initialize_home()
        players.append(player)

    game = Game(players, section_length=4)
    game.initialize()

    prehome_positions = {}
    for symbol in symbols:
        prehome_positions[symbol] = \
            game.get_player(symbol).get_prehome_position()

    def test_update_board_waiting(self):
        modified_game = deepcopy(self.game)
        modified_game.set_waiting_count_array('2', count=0)

        assert modified_game.board.waiting_count['2'] == 0

    def test_update_board_spaces(self):
        modified_game = deepcopy(self.game)
        occupied_position = modified_game.get_player('3').get_start_position()
        modified_game.set_space_array('1', occupied_position)

        assert modified_game.board.spaces[occupied_position] == '1'

    def test_update_board_homes(self):
        modified_game = deepcopy(self.game)
        modified_game.set_homes_array('1', 1)

        assert (
            modified_game.board.homes['1']
            == [EMPTY_VALUE, '1', EMPTY_VALUE, EMPTY_VALUE]
        )

    def test_get_symbol_space_position_array(self):
        modified_game = deepcopy(self.game)
        modified_game.set_space_array('1', 0)
        modified_game.set_space_array('2', 1)

        assert modified_game.get_symbol_space_positions('1') == np.array([0])
        assert modified_game.get_symbol_space_positions('2') == np.array([1])

    # Leave home move tests
    def test_leave_home_is_valid(self):
        for symbol in ['1', '4']:
            assert self.game.leave_home_is_valid(
                symbol=symbol, roll=NR_OF_DICE_FACES
            )
            # Any other roll is invalid to leave home
            for roll in range(1, NR_OF_DICE_FACES):
                assert not (
                    self.game.leave_home_is_valid(symbol=symbol, roll=roll)
                )

    def test_get_leave_home_moves(self):
        modified_game = deepcopy(self.game)

        symbol = '1'
        roll = NR_OF_DICE_FACES
        player = modified_game.get_player(symbol)
        player_start_space = player.get_start_position()
        expected = [Move(symbol, 'leave_home', end=player_start_space)]

        assert modified_game.get_leave_home_moves(symbol, roll) == expected

    @pytest.mark.parametrize(
        'symbol,roll',
        [
            ('1', 1),
            ('2', NR_OF_DICE_FACES),
            ('3', NR_OF_DICE_FACES)
        ]
    )
    def test_no_get_leave_home_moves(self, symbol, roll):
        modified_game = deepcopy(self.game)

        modified_game.set_waiting_count_array('2', 0)
        modified_game.set_space_array(
             '1', modified_game.get_player(symbol).get_start_position()
        )

        assert modified_game.get_leave_home_moves(symbol, roll) == []

    # Test space advance moves
    @pytest.mark.parametrize(
        'symbol,position,roll,expected',
        [
            ('1', 0, 3, True),
            ('2', 0, 3, True),
            ('2', 0, 4, False),
            ('1', prehome_positions['1'] - 1, 1, True),
            ('1', prehome_positions['1'], 1, False)
        ]
    )
    def test_is_space_advance_move(self, symbol, position, roll, expected):
        assert (
            self.game.is_space_advance_move(
                symbol=symbol, position=position, roll=roll
            ) == expected
        )

    @pytest.mark.parametrize(
        'symbol,position,roll,expected',
        [
            ('1', 0, 1, True),
            ('1', 8 - 1, 1, False)  # see in test definition
        ]
    )
    def test_space_advance_is_valid(self, symbol, position, roll, expected):
        modified_game = deepcopy(self.game)
        modified_game.set_space_array('1', 8)
        assert modified_game.space_advance_is_valid(symbol, position, roll) \
            == expected

    def test_get_space_advance_moves(self):
        modified_game = deepcopy(self.game)

        symbol = '1'
        modified_game.set_space_array(symbol, 0)
        modified_game.set_space_array(symbol, 1)

        roll = 1

        assert (
            modified_game.get_space_advance_moves(symbol, roll)
            == [Move(symbol, 'space_advance', start=1, end=2)]
        )

    # Test space to home moves
    @pytest.mark.parametrize(
        'symbol,position,roll,expected',
        [
            ('1', prehome_positions['1'], 1, True),
            ('1', prehome_positions['1'] - 1, 1, False),
            # Note: is move methods ignore validity
            ('1', prehome_positions['1'] - 1, PIECES_PER_PLAYER, True)
        ]
    )
    def test_is_space_to_home(self, symbol, position, roll, expected):
        assert self.game.is_space_to_home_move(symbol, position, roll) \
            == expected

    @pytest.mark.parametrize(
        'symbol,position,roll,expected',
        [
            ('1', prehome_positions['1'], 1, True),
            ('2', 3, 1, True),
            ('1', prehome_positions['1'], PIECES_PER_PLAYER + 1, False),
            ('3', prehome_positions['3'], 1, False)  # occupied
        ]
    )
    def test_space_to_home_is_valid(self, symbol, position, roll, expected):
        modified_game = deepcopy(self.game)

        if symbol == '3':
            modified_game.set_homes_array(symbol, 1)

        assert modified_game.space_to_home_is_valid(
            symbol, position, roll
        ) == expected

    @pytest.mark.parametrize(
        'symbol,position,roll,expected',
        [
            ('1', prehome_positions['1'], PIECES_PER_PLAYER + 1, []),
            (
                '1', prehome_positions['1'], 1,
                [
                    Move(
                        '1', 'space_to_home',
                        start=prehome_positions['1'], end=0)
                ]
            ),
            ('1', prehome_positions['1'] - 1, 1, []),

        ]
    )
    def test_get_space_to_home_moves(self, symbol, position, roll, expected):
        modified_game = deepcopy(self.game)
        modified_game.set_space_array(symbol, position)

        assert (
            modified_game.get_space_to_home_moves(symbol, roll)
            == expected
        )

    def test_get_symbol_home_array(self):
        modified_game = deepcopy(self.game)
        symbol = '1'
        modified_game.set_homes_array(symbol, position=0)
        modified_game.set_homes_array(symbol, position=3)

        np.testing.assert_array_equal(
            modified_game.get_symbol_home_positions(symbol),
            np.array([0, 3])
        )

    @pytest.mark.parametrize(
        'position',
        [(2), (2), (3)]
    )
    def test_get_home_positions(self, position):
        modified_game = deepcopy(self.game)
        symbol = '1'
        # Occupy position 1 for all tests
        modified_game.set_homes_array(symbol, position=0)
        modified_game.set_homes_array(symbol, position)

        np.testing.assert_array_equal(
            modified_game.get_symbol_home_positions(symbol),
            np.array([0, position])
        )

    @pytest.mark.parametrize(
        'symbol,position,roll,expected',
        [
            ('1', 0, 1, True),
            # Occupied
            ('1', 0, 2, False),
            ('1', 2, 1, True),
            # Beyond home spaces
            ('1',  0, 4, False)
        ]
    )
    def test_home_advance_is_valid(self, symbol, position, roll, expected):
        modified_game = deepcopy(self.game)
        modified_game.set_homes_array(symbol, position=0)
        modified_game.set_homes_array(symbol, position=2)

        assert modified_game.home_advance_is_valid(symbol, position, roll) \
            == expected

    @pytest.mark.parametrize(
        'symbol,roll,expected',
        [
            ('1', 1, [
                Move('1', 'home_advance', start=0, end=0+1),
                Move('1', 'home_advance', start=2, end=2+1)
            ]),
            # Blocked by occupation and beyond home spaces
            ('1', 2, [])
        ]
    )
    def test_get_home_advance_moves(self, symbol, roll, expected):
        modified_game = deepcopy(self.game)
        modified_game.set_homes_array(symbol, position=0)
        modified_game.set_homes_array(symbol, position=2)

        assert modified_game.get_home_advance_moves(symbol, roll) \
            == expected
