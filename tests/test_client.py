"""Tests for clovek_ne_jezi_se.Client"""
import builtins
from copy import deepcopy

import pytest

from clovek_ne_jezi_se.client import Client
from clovek_ne_jezi_se.agent import HumanPlayer
from clovek_ne_jezi_se.game_state import (
    GameState, MoveContainer, BoardSpace,
    EMPTY_SYMBOL
)


def get_main_spaces_as_list(game_state: 'GameState') -> list:
    """Convenience function for testing equality of main board spaces"""
    res = []
    for idx in range(game_state.section_length * len(game_state.player_names)):
        main_space_dict = dict(
            kind='main', idx=idx
        )
        main_space = game_state.get_board_space(**main_space_dict)
        res.append(main_space.occupied_by)
    return res


def get_game_state_counts(game_state: 'GameState', kind: str):
    """
    Convenience function for testing equality of game states

    Parameters
    ----------
    kind :
        One of 'waiting' or 'home'
    """
    res = {}
    for player_name in game_state.player_names:
        count = 0
        for idx in range(game_state.pieces_per_player):
            space_dict = dict(
                kind=kind, idx=idx, player_name=player_name
            )
            space = game_state.get_board_space(**space_dict)
            if space.occupied_by == player_name:
                count += 1
        res[player_name] = count
    return res


class TestGetGameSpaceSummaries:
    player_names = ['red', 'blue', 'green', 'yellow']
    players = [HumanPlayer(name=name) for name in player_names]

    client = Client(players=players)
    client.initialize()
    game_state = client.get_game_state()

    @pytest.mark.parametrize(
        'kind,expected',
        [
            ('waiting', dict(red=4, blue=4, green=4, yellow=4)),
            ('home', dict(red=0, blue=0, green=0, yellow=0))
        ]
    )
    def test_get_waiting_area_counts(self, kind, expected):
        res = get_game_state_counts(self.game_state, kind)
        assert res == expected

    def test_get_main_spaces_as_list(self):
        res = get_main_spaces_as_list(self.game_state)
        expected = self.game_state.section_length \
            * len(self.game_state.player_names) \
            * [EMPTY_SYMBOL]

        assert res == expected


def monkey_roll(roll_value):
    """Monkeypatch for dice roll"""
    return roll_value


class TestClient:
    player_names = ['red', 'blue', 'green', 'yellow']
    players = [HumanPlayer(name=name) for name in player_names]

    client = Client(players=players)
    client.initialize()

    def test_initial_state(self):
        expected_game_state = GameState(self.player_names)

        assert self.client.get_game_state() == expected_game_state

    def test_next_player(self):
        player_round = [
            self.client.next_player() for _ in range(len(self.player_names))
        ]

        assert player_round == self.players

    def test_dice_roll_monkeypatch(self, monkeypatch):
        value = 1
        monkeypatch.setattr(self.client, 'roll', lambda: monkey_roll(value))
        assert self.client.roll() == value

    def test_integration(self, monkeypatch):

        played_client = deepcopy(self.client)
        expected_game_state = deepcopy(self.client.get_game_state())

        # Set roll value to 6
        monkeypatch.setattr(played_client, 'roll', lambda: monkey_roll(6))
        # For HumanAgent choose_move input, always select 0th
        idx_move_input = 0
        monkeypatch.setattr(builtins, 'input', lambda x: idx_move_input)

        # Play one round with fixed (monkeypatched) dice and move choice
        for _ in range(len(played_client.players)):
            played_client.play()

        # Move 0th piece to main board from waiting for each player
        for player_name in self.client._player_names:
            expected_game_state.do(MoveContainer(
                from_space=BoardSpace(
                    kind='waiting', idx=0, occupied_by=player_name,
                    allowed_occupants=[player_name, EMPTY_SYMBOL]
                ),
                to_space=BoardSpace(
                    kind='main',
                    idx=expected_game_state.get_main_entry_index(player_name),
                    occupied_by=EMPTY_SYMBOL,
                    allowed_occupants=self.player_names + [EMPTY_SYMBOL]

                )
            ))

        played_game_state = played_client.get_game_state()

        played_waiting_counts = get_game_state_counts(
            played_game_state, 'waiting'
        )
        expected_waiting_counts = get_game_state_counts(
            expected_game_state, 'waiting'
        )

        assert played_waiting_counts == expected_waiting_counts

        played_main_spaces = get_main_spaces_as_list(played_game_state)
        expected_main_spaces = get_main_spaces_as_list(expected_game_state)

        assert played_main_spaces == expected_main_spaces

        played_home_counts = get_game_state_counts(
            played_game_state, 'home'
        )
        expected_home_counts = get_game_state_counts(
            expected_game_state, 'home'
        )

        assert played_home_counts == expected_home_counts
