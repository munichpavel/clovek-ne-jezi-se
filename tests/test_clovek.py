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
    def test_player_mini_start(
        self, symbol, expected_position
    ):
        # Mini board
        assert (
            self.mini_game.get_player(symbol).get_start()
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
    def test_player_normal_start(
        self, symbol, expected_position
    ):
        # Normal board
        assert (
            self.full_game.get_player(symbol).get_start()
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
            Move('1', 'nonsense_move', roll=5, start=0)

        # Start position must be None for leave_waiting move
        with pytest.raises(ValueError):
            Move('1', 'leave_waiting', roll=6, start=0)


class TestGameAction:
    symbols = ['1', '2', '3', '4']
    players = []
    for symbol in symbols:
        player = Player(symbol=symbol, number_of_players=4)
        player.initialize_home()
        players.append(player)

    game = Game(players, section_length=4)
    game.initialize()

    # Useful board space positions for test cases
    starts = {}
    prehome_positions = {}
    for symbol in symbols:
        player = game.get_player(symbol)
        starts[symbol] = player.get_start()
        prehome_positions[symbol] = player.get_prehome_position()

    def test_get_symbol_space_position_array(self):
        modified_game = deepcopy(self.game)
        modified_game.set_space_array('1', 0)
        modified_game.set_space_array('2', 1)

        assert modified_game.get_symbol_space_positions('1') == np.array([0])
        assert modified_game.get_symbol_space_positions('2') == np.array([1])

    # Test moves
    @pytest.mark.parametrize(
        'arg_dict,expected',
        [
            (
                dict(symbol='1', move_kind='leave_waiting', roll=6),
                Move('1', 'leave_waiting', roll=6)
            ),
            (
                dict(symbol='1', move_kind='space_advance', roll=1, start=0),
                Move('1', 'space_advance', roll=1, start=0)
            ),
            (
                dict(
                    symbol='1', move_kind='space_to_home',
                    roll=1, start=prehome_positions['1']
                ),
                Move(
                    '1', 'space_to_home', roll=1, start=prehome_positions['1']
                )
            ),
            (
                dict(symbol='1', move_kind='home_advance', roll=1, start=0),
                Move('1', 'home_advance', roll=1, start=0)
            ),
        ]
    )
    def test_move_factory(self, arg_dict, expected):
        move = self.game.move_factory(**arg_dict)
        assert move == expected

    def test_move_factory_errors(self):
        modified_game = deepcopy(self.game)
        modified_game.set_space_array('2', self.starts['2'])

        symbol = '1'
        move_kind = 'space_advance'
        roll = 1
        move_start = self.starts['2'] - roll

        with pytest.raises(ValueError):
            modified_game.move_factory(symbol, move_kind, roll, move_start)

    # Leave home move tests
    def test_leave_waiting_is_valid(self):
        for symbol in ['1', '4']:
            assert self.game.leave_waiting_is_valid(
                symbol=symbol, roll=NR_OF_DICE_FACES
            )
            # Any other roll is invalid to leave home
            for roll in range(1, NR_OF_DICE_FACES):
                assert not (
                    self.game.leave_waiting_is_valid(symbol=symbol, roll=roll)
                )

    def test_get_leave_waiting_moves(self):
        modified_game = deepcopy(self.game)

        symbol = '1'
        roll = NR_OF_DICE_FACES
        expected = [Move(symbol, 'leave_waiting', roll=roll)]

        assert modified_game.get_leave_waiting_moves(symbol, roll) == expected

    @pytest.mark.parametrize(
        'symbol,roll',
        [
            ('1', 1),
            ('2', NR_OF_DICE_FACES),
            ('3', NR_OF_DICE_FACES)
        ]
    )
    def test_no_get_leave_waiting_moves(self, symbol, roll):
        modified_game = deepcopy(self.game)

        modified_game.set_waiting_count_array('2', 0)
        modified_game.set_space_array(
             '1', modified_game.get_player(symbol).get_start()
        )

        assert modified_game.get_leave_waiting_moves(symbol, roll) == []

    # Test space advance moves
    @pytest.mark.parametrize(
        'symbol,roll,position,expected',
        [
            ('1', 3, 0, True),
            ('2', 3, 0, True),
            ('2', 4, 0, False),
            ('1', 1, prehome_positions['1'] - 1, True),
            ('1', 1, prehome_positions['1'], False)
        ]
    )
    def test_is_space_advance_move(self, symbol, roll, position, expected):
        assert (
            self.game.is_space_advance_move(
                symbol, roll, position
            ) == expected
        )

    @pytest.mark.parametrize(
        'symbol,roll,position,expected',
        [
            ('1', 1, 0, True),
            ('1', 1, 8 - 1, False)  # see in test definition
        ]
    )
    def test_space_advance_not_blocked(self, symbol, roll, position, expected):
        modified_game = deepcopy(self.game)
        modified_game.set_space_array('1', 8)
        assert modified_game.space_advance_not_blocked(symbol, roll, position) \
            == expected

    def test_get_space_advance_moves(self):
        modified_game = deepcopy(self.game)

        symbol = '1'
        modified_game.set_space_array(symbol, 0)
        modified_game.set_space_array(symbol, 1)

        roll = 1

        assert (
            modified_game.get_space_advance_moves(symbol, roll)
            == [Move(symbol, 'space_advance', roll=1, start=1)]
        )

    # Test space to home moves
    @pytest.mark.parametrize(
        'symbol,roll,position,expected',
        [
            ('1', 1, prehome_positions['1'], True),
            ('1', 1, prehome_positions['1'] - 1, False),
            # Note: is move methods ignore validity
            ('1', PIECES_PER_PLAYER, prehome_positions['1'] - 1, True)
        ]
    )
    def test_is_space_to_home(self, symbol, roll, position, expected):
        assert self.game.is_space_to_home_move(symbol, roll, position) \
            == expected

    @pytest.mark.parametrize(
        'symbol,roll,position,expected',
        [
            ('1', 1, prehome_positions['1'], True),
            ('2', 1, 3, True),
            ('1', PIECES_PER_PLAYER + 1, prehome_positions['1'], False),
            ('3', 1, prehome_positions['3'], False)  # occupied
        ]
    )
    def test_space_to_home_is_valid(self, symbol, roll, position, expected):
        modified_game = deepcopy(self.game)

        if symbol == '3':
            modified_game.set_homes_array(symbol, 1)

        assert modified_game.space_to_home_is_valid(
            symbol, roll, position
        ) == expected

    @pytest.mark.parametrize(
        'symbol,roll,position,expected',
        [
            ('1', PIECES_PER_PLAYER + 1, prehome_positions['1'], []),
            (
                '1', 1, prehome_positions['1'],
                [
                    Move(
                        '1', 'space_to_home', roll=1,
                        start=prehome_positions['1'])
                ]
            ),
            ('1', 1, prehome_positions['1'] - 1, []),

        ]
    )
    def test_get_space_to_home_moves(self, symbol, roll, position, expected):
        modified_game = deepcopy(self.game)
        modified_game.set_space_array(symbol, position)
        print(roll, position)

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
        'symbol,roll,position,expected',
        [
            ('1', 1, 0, True),
            # Occupied
            ('1', 2, 0, False),
            ('1', 1, 2, True),
            # Beyond home spaces
            ('1',  4, 0, False)
        ]
    )
    def test_home_advance_is_valid(self, symbol, roll, position, expected):
        modified_game = deepcopy(self.game)
        modified_game.set_homes_array(symbol, position=0)
        modified_game.set_homes_array(symbol, position=2)

        assert modified_game.home_advance_is_valid(symbol, roll, position) \
            == expected

    @pytest.mark.parametrize(
        'symbol,roll,expected',
        [
            ('1', 1, [
                Move('1', 'home_advance', roll=1, start=0),
                Move('1', 'home_advance', roll=1, start=2)
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

    # def test_do(self):
    #     modified_game = deepcopy(self.game)
    #     symbol = '1'

    #     end = modified_game.get_player(symbol).get_start()
    #     move = Move(symbol, 'leave_waiting')

    #     modified_game.do(move)

    #     expected_game = deepcopy(self.game)
    #     expected_game.set_waiting_count_array(symbol, 3)
    #     expected_game.set_space_array(symbol, end)

    #     self.assert_board_state_equal(modified_game, expected_game)

    def assert_board_state_equal(self, board_1, board_2):
        np.testing.assert_array_equal(
            board_1.get_waiting_count_array(),
            board_2.get_waiting_count_array()
        )

        np.testing.assert_array_equal(
            board_1.get_spaces_array(),
            board_2.get_spaces_array()
        )

        np.testing.assert_array_equal(
            board_1.get_homes_array(),
            board_2.get_homes_array()
        )

    # Board representation tests
    def test_update_board_waiting(self):
        modified_game = deepcopy(self.game)
        modified_game.set_waiting_count_array('2', count=0)

        assert modified_game.board.waiting_count['2'] == 0

    def test_update_board_spaces(self):
        modified_game = deepcopy(self.game)
        occupied_position = modified_game.get_player('3').get_start()
        modified_game.set_space_array('1', occupied_position)

        assert modified_game.board.spaces[occupied_position] == '1'

    def test_update_board_homes(self):
        modified_game = deepcopy(self.game)
        modified_game.set_homes_array('1', 1)

        assert (
            modified_game.board.homes['1']
            == [EMPTY_VALUE, '1', EMPTY_VALUE, EMPTY_VALUE]
        )
