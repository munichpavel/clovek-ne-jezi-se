"""Tests for agents, if not already tested in test_client."""
from copy import deepcopy

from clovek_ne_jezi_se.client import Client
from clovek_ne_jezi_se.game_state import (
    MoveContainer, BoardSpace, EMPTY_SYMBOL
)
from clovek_ne_jezi_se.agents import FurthestAlongPlayer


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

        played_waiting = played_game_state.waiting_areas_to_dict()
        expected_waiting = expected_game_state.waiting_areas_to_dict()

        assert played_waiting == expected_waiting

        played_main_spaces = played_game_state.main_spaces_to_list()
        expected_main_spaces = expected_game_state.main_spaces_to_list()

        assert played_main_spaces == expected_main_spaces

        played_home = played_game_state.home_areas_to_dict()
        expected_home = expected_game_state.home_areas_to_dict()

        assert played_home == expected_home

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

        played_waiting = played_game_state.waiting_areas_to_dict()
        expected_waiting = expected_game_state.waiting_areas_to_dict()

        assert played_waiting == expected_waiting

        played_main_spaces = played_game_state.main_spaces_to_list()
        expected_main_spaces = expected_game_state.main_spaces_to_list()

        assert played_main_spaces == expected_main_spaces

        played_home = played_game_state.home_areas_to_dict()
        expected_home = expected_game_state.home_areas_to_dict()

        assert played_home == expected_home
