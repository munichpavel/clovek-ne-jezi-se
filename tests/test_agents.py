"""Tests for agents, if not already tested in test_client."""
from copy import deepcopy

import pytest

from clovek_ne_jezi_se.client import Client
from clovek_ne_jezi_se.game_state import (
    GameState, MoveContainer, BoardSpace, EMPTY_SYMBOL
)
from clovek_ne_jezi_se.agents import FurthestAlongPlayer


def assert_game_states_equal(
    game_state: 'GameState', other: 'GameState'
):
    waiting = game_state.waiting_areas_to_dict()
    other_waiting = other.waiting_areas_to_dict()

    assert waiting == other_waiting

    main = game_state.main_spaces_to_list()
    other_main = other.main_spaces_to_list()

    assert main == other_main

    home = game_state.home_areas_to_dict()
    other_home = other.home_areas_to_dict()

    assert home == other_home


def test_assert_game_states_equal():
    # Set attributes for repeated use below
    player_names = ['red', 'blue', 'green', 'yellow']
    pieces_per_player = 4
    section_length = 4
    game_state = GameState(
        player_names=player_names, pieces_per_player=pieces_per_player,
        section_length=section_length
    )
    game_state.initialize()

    assert_game_states_equal(game_state, game_state)

    other = deepcopy(game_state)
    other.do(MoveContainer(
            from_space=BoardSpace(
                kind='waiting', idx=0,
                occupied_by='red',
                allowed_occupants=['red', EMPTY_SYMBOL]
            ),
            to_space=BoardSpace(
                kind='main', idx=0,
                occupied_by=EMPTY_SYMBOL,
                allowed_occupants=player_names + [EMPTY_SYMBOL]
            )
        ))

    with pytest.raises(AssertionError):
        assert_game_states_equal(game_state, other)


class TestAgents:
    player_names = ['red']
    players = [
        FurthestAlongPlayer(name=name, print_game_state=False)
        for name in player_names
    ]

    client = Client(players=players)
    client.initialize()

    def test_furthest_along_choose_move(self, monkeypatch):
        played_client = deepcopy(self.client)
        expected_client = deepcopy(self.client)

        # Move red players to main board
        played_game_state = played_client.get_game_state()
        idx_main_ahead = 3
        idx_main_behind = 1
        idx_home = played_game_state.pieces_per_player-2
        played_game_state.do(MoveContainer(
            from_space=BoardSpace(
                kind='waiting', idx=0,
                occupied_by='red',
                allowed_occupants=['red', EMPTY_SYMBOL]
            ),
            to_space=BoardSpace(
                kind='main', idx=idx_main_ahead,
                occupied_by=EMPTY_SYMBOL,
                allowed_occupants=self.player_names + [EMPTY_SYMBOL]
            )
        ))
        played_game_state.do(MoveContainer(
            from_space=BoardSpace(
                kind='waiting', idx=1,
                occupied_by='red',
                allowed_occupants=['red', EMPTY_SYMBOL]
            ),
            to_space=BoardSpace(
                kind='main', idx=idx_main_behind,
                occupied_by=EMPTY_SYMBOL,
                allowed_occupants=self.player_names + [EMPTY_SYMBOL]
            )
        ))
        played_game_state.do(MoveContainer(
            from_space=BoardSpace(
                kind='waiting', idx=2,
                occupied_by='red',
                allowed_occupants=['red', EMPTY_SYMBOL]
            ),
            to_space=BoardSpace(
                kind='home', idx=idx_home,
                occupied_by=EMPTY_SYMBOL,
                allowed_occupants=['red', EMPTY_SYMBOL]
            )
        ))

        # Set roll value to 1
        roll = 1
        monkeypatch.setattr(played_client, 'roll', lambda: roll)

        # Play once (red) with fixed (monkeypatched) dice
        played_client.take_turn()

        expected_game_state = expected_client.get_game_state()

        expected_game_state.do(MoveContainer(
            from_space=BoardSpace(
                kind='waiting', idx=0, occupied_by='red',
                allowed_occupants=['red', EMPTY_SYMBOL]
            ),
            to_space=BoardSpace(
                kind='main', idx=idx_main_ahead,
                occupied_by='red',
                allowed_occupants=self.player_names + [EMPTY_SYMBOL]
            )
        ))
        expected_game_state.do(MoveContainer(
            from_space=BoardSpace(
                kind='waiting', idx=1, occupied_by='red',
                allowed_occupants=['red', EMPTY_SYMBOL]
            ),
            to_space=BoardSpace(
                kind='main', idx=idx_main_behind,
                occupied_by='red',
                allowed_occupants=self.player_names + [EMPTY_SYMBOL]

            )
        ))
        expected_game_state.do(MoveContainer(
            from_space=BoardSpace(
                kind='waiting', idx=2,
                occupied_by='red',
                allowed_occupants=['red', EMPTY_SYMBOL]
            ),
            to_space=BoardSpace(
                kind='home', idx=idx_home + roll,
                occupied_by=EMPTY_SYMBOL,
                allowed_occupants=['red', EMPTY_SYMBOL]
            )
        ))

        assert_game_states_equal(played_game_state, expected_game_state)

        # Play again red with fixed (monkeypatched) dice
        played_client.take_turn()

        expected_game_state.do(MoveContainer(
            from_space=BoardSpace(
                kind='main', idx=idx_main_ahead,
                occupied_by='red',
                allowed_occupants=self.player_names + [EMPTY_SYMBOL]
            ),
            to_space=BoardSpace(
                kind='main', idx=idx_main_ahead + roll,
                occupied_by='red',
                allowed_occupants=self.player_names + [EMPTY_SYMBOL]
            )
        ))

        assert_game_states_equal(played_game_state, expected_game_state)
