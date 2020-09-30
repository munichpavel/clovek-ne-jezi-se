"""Tests for `clovek_ne_jezi_se` package."""
from copy import deepcopy
import pytest

import numpy as np

from clovek_ne_jezi_se.consts import (
    EMPTY_SYMBOL, PIECES_PER_PLAYER, NR_OF_DICE_FACES
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
                == PIECES_PER_PLAYER * [EMPTY_SYMBOL]
            )

    def test_player_representation(self, small_initial_board):
        for symbol in ['1', '2', '3', '4', EMPTY_SYMBOL]:
            assert small_initial_board.get_public_symbol(
                small_initial_board.get_private_symbol(symbol)
             ) == symbol


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
            self.mini_game.get_player(symbol).get_leave_waiting_position()
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
            self.full_game.get_player(symbol).get_leave_waiting_position()
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
            Move('1', 'leave_waiting', roll=NR_OF_DICE_FACES, start=0)


class TestGameAction:
    symbols = ['1', '2', '3', '4']
    players = []
    for symbol in symbols:
        player = Player(symbol=symbol, number_of_players=4)
        player.initialize_home()
        players.append(player)

    game = Game(players, section_length=4)
    game.initialize()

    # Define board space position variables for test cases
    leave_waiting_positions = {}
    prehome_positions = {}
    for symbol in symbols:
        player = game.get_player(symbol)
        leave_waiting_positions[symbol] = player.get_leave_waiting_position()
        prehome_positions[symbol] = player.get_prehome_position()

    # Get position methods
    def test_get_symbol_waiting_count(self):
        assert self.game.get_symbol_waiting_count('1') == PIECES_PER_PLAYER

        modified_game = deepcopy(self.game)
        modified_game.set_waiting_count_array('1', 0)
        assert modified_game.get_symbol_waiting_count('1') == 0

    def test_get_symbol_space_position_array(self):
        modified_game = deepcopy(self.game)
        modified_game.set_space_array('1', 0)
        modified_game.set_space_array('2', 1)

        assert modified_game.get_symbol_space_array('1') == np.array([0])
        assert modified_game.get_symbol_space_array('2') == np.array([1])

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

    @pytest.mark.parametrize('position,symbol', [(0, '1'), (1, EMPTY_SYMBOL)])
    def test_get_space_occupier(self, position, symbol):
        modified_game = deepcopy(self.game)
        modified_game.set_space_array('1', 0)

        assert modified_game.get_space_occupier(position) == symbol

    @pytest.mark.parametrize(
        'symbol,position,expected',
        [
            ('1', leave_waiting_positions['1'], 0),
            ('1', prehome_positions['1'], 16 - 1),  # Board with 16 spaces
            ('2', leave_waiting_positions['2'], 0),
            ('2', prehome_positions['2'], 16 - 1),  # Board with 16 spaces

        ]
    )
    def test_get_zeroed_position(self, symbol, position, expected):
        assert self.game.get_zeroed_position(symbol, position) == expected

    @pytest.mark.parametrize(
        'symbol,roll,start,expected',
        [
            ('1', 1, prehome_positions['1'], 0),
            ('1', 4, prehome_positions['1'], 3)
        ]
    )
    def test_get_space_to_home_position(self, symbol, roll, start, expected):
        assert self.game.get_space_to_home_position(symbol, roll, start) \
            == expected

    # Test moves
    @pytest.mark.parametrize(
        'arg_dict,expected',
        [
            (
                dict(symbol='1', kind='leave_waiting', roll=NR_OF_DICE_FACES),
                [
                    Move('1', 'leave_waiting', roll=NR_OF_DICE_FACES),
                    Move(
                        '2', 'return_to_waiting',
                        start=leave_waiting_positions['1']
                    )
                ]
            ),
            (
                dict(
                    symbol='2', kind='space_advance',
                    roll=1, start=prehome_positions['1'] - 1
                ),
                [
                    Move('2', 'space_advance',
                         roll=1, start=prehome_positions['1'] - 1),
                    Move(
                        '1', 'return_to_waiting',
                        start=prehome_positions['1']
                    )
                ]
            ),
            (
                dict(symbol='1', kind='space_advance', roll=1, start=1),
                [Move('1', 'space_advance', roll=1, start=1)]
            ),
            (
                dict(
                    symbol='1', kind='space_to_home',
                    roll=1, start=prehome_positions['1']
                ),
                [Move(
                    '1', 'space_to_home', roll=1, start=prehome_positions['1']
                )]
            ),
            (
                dict(symbol='1', kind='home_advance', roll=1, start=0),
                [Move('1', 'home_advance', roll=1, start=0)]
            ),
        ]
    )
    def test_move_factory(self, arg_dict, expected):
        modified_game = deepcopy(self.game)

        modified_game.set_space_array('1', 1)
        modified_game.set_space_array('1', self.prehome_positions['1'])
        modified_game.set_waiting_count_array('1', PIECES_PER_PLAYER - 2)

        modified_game.set_space_array('2', self.leave_waiting_positions['1'])
        modified_game.set_space_array('2', self.prehome_positions['1'] - 1)
        modified_game.set_waiting_count_array('2', PIECES_PER_PLAYER - 1)

        move = modified_game.move_factory(**arg_dict)

        # TODO reduce flakiness potential from equality of lists condition
        assert move == expected

    @pytest.mark.parametrize(
        'symbol,kind,roll,start',
        [
            ('1', 'leave_waiting', NR_OF_DICE_FACES, None),  # Waiting count 0
            ('1', 'leave_waiting', 1, None),  # Invalid roll
            # Occupied by own piece
            ('2', 'leave_waiting', NR_OF_DICE_FACES, None),
            ('1', 'space_advance', 0, 1),  # Start not occupied by '1'
            # End occupied
            ('1', 'space_advance', 1, leave_waiting_positions['2'] - 1),
            ('1', 'space_advance', 1, prehome_positions['1']),  # Space to home
            (
                '1', 'space_to_home',
                PIECES_PER_PLAYER + 1, prehome_positions['1']
            ),  # Beyond last home space
            ('3', 'space_to_home', 1, prehome_positions['3']),  # Occupied
            ('4', 'home_advance', 1, 1),  # Occupied
            ('4', 'home_advance', PIECES_PER_PLAYER, 0)  # Beyond last space
        ]
    )
    def test_move_factory_errors(self, symbol, kind, roll, start):
        modified_game = deepcopy(self.game)
        modified_game.set_waiting_count_array('1', 0)

        modified_game.set_space_array('2', self.leave_waiting_positions['2'])

        modified_game.set_homes_array('3', 0)
        modified_game.set_homes_array('4', 2)

        with pytest.raises(ValueError):
            modified_game.move_factory(symbol, kind, roll, start)

    @pytest.mark.parametrize(
        'symbol,kind,roll,expected',
        [
            (
                '1', 'leave_waiting', NR_OF_DICE_FACES,
                [Move('1', 'leave_waiting', roll=NR_OF_DICE_FACES)]
            ),
            ('2', 'leave_waiting', NR_OF_DICE_FACES, []),  # No pieces left
            (
                '2', 'space_advance', 1,
                [Move(
                    '2', 'space_advance', roll=1,
                    start=leave_waiting_positions['2']
                )]
            ),
            ('1', 'space_advance', 1, []),  # No players to advance
            (
                '3', 'space_to_home', 1,
                [
                    Move('3', 'space_to_home', roll=1,
                         start=prehome_positions['3'])
                ]
            ),
            ('1', 'space_to_home', 1, []),  # No players to advance
            (
                '4', 'home_advance', 1,
                [Move('4', 'home_advance', roll=1, start=1)]
            ),
            ('4', 'home_advance', 2, []),  # Occupied
        ]
    )
    def test_get_moves_of(self, symbol, kind, roll, expected):
        modified_game = deepcopy(self.game)
        modified_game.set_waiting_count_array('2', 0)
        modified_game.set_space_array(
             '2', self.leave_waiting_positions['2']
        )
        modified_game.set_space_array(
             '3', self.prehome_positions['3']
        )
        modified_game.set_homes_array('4', 1)
        modified_game.set_homes_array('4', 3)

        moves = modified_game.get_moves_of(symbol, kind, roll)

        assert moves == expected

    def test_game_state_is_equal(self):
        """Test game state equality method"""
        assert game_state_is_equal(self.game, self.game)

        modified_waiting = deepcopy(self.game)
        modified_waiting.set_waiting_count_array('1', 0)
        assert not game_state_is_equal(self.game, modified_waiting)

        modified_spaces = deepcopy(self.game)
        modified_spaces.set_space_array('1', 0)
        assert not game_state_is_equal(self.game, modified_spaces)

        modified_homes = deepcopy(self.game)
        modified_homes.set_space_array('1', 0)
        assert not game_state_is_equal(self.game, modified_homes)

    def test_do(self):
        modified_game = deepcopy(self.game)
        expected_game = deepcopy(self.game)

        # Prepopulate board
        for game in [modified_game, expected_game]:
            game.set_space_array('2', self.leave_waiting_positions['1'])
            game.set_waiting_count_array('2', PIECES_PER_PLAYER - 1)

            game.set_space_array('4', self.prehome_positions['4'])
            game.set_waiting_count_array('4', PIECES_PER_PLAYER - 1)

        # Leave waiting and send opponent piece back to waiting
        modified_game.do('1', 'leave_waiting', roll=NR_OF_DICE_FACES)
        expected_game.set_waiting_count_array('1', PIECES_PER_PLAYER - 1)
        pre_move_waiting_count = expected_game.get_symbol_waiting_count('2')
        expected_game.set_waiting_count_array('2',  pre_move_waiting_count + 1)
        expected_game.set_space_array('1', self.leave_waiting_positions['1'])

        assert game_state_is_equal(modified_game, expected_game)

        # Blocked by own
        modified_game.do('1', 'leave_waiting', roll=NR_OF_DICE_FACES)
        assert game_state_is_equal(modified_game, expected_game)

        # Space to home move
        modified_game.do(
            '4', 'space_to_home', roll=1, start=self.prehome_positions['4']
        )
        expected_game.set_space_array(
            EMPTY_SYMBOL, self.prehome_positions['4']
        )
        expected_game.set_homes_array('4', 0)

        assert game_state_is_equal(modified_game, expected_game)

    # Board representation tests
    def test_update_board_spaces(self):
        modified_game = deepcopy(self.game)
        occupied_position = (
            modified_game.get_player('3').get_leave_waiting_position()
        )
        modified_game.set_space_array('1', occupied_position)

        assert modified_game.board.spaces[occupied_position] == '1'

    def test_update_board_homes(self):
        modified_game = deepcopy(self.game)
        modified_game.set_homes_array('1', 1)

        assert (
            modified_game.board.homes['1']
            == [EMPTY_SYMBOL, '1', EMPTY_SYMBOL, EMPTY_SYMBOL]
        )


def game_state_is_equal(game_1, game_2):
    """
    Convenience method for testing game states.

    Parameters
    ----------
    board_1 : triple of np.arrays
        Triple of waiting counts array, spaces array and home array
    board_2 : triple of np.arrays
        Triple of waiting counts array, spaces array and home array

    Returns
    -------
    res : Boolean
        board_1 == board_2
    """
    res = []
    res.append(np.array_equal(
        game_1.get_waiting_count_array(),
        game_2.get_waiting_count_array()
        ))

    print(game_1.get_spaces_array(), game_2.get_spaces_array())
    res.append(np.array_equal(
        game_1.get_spaces_array(),
        game_2.get_spaces_array()
    ))

    res.append(np.array_equal(
        game_1.get_homes_array(),
        game_2.get_homes_array()
    ))
    print(res)
    return np.all(np.array(res))
