"""Tests for clovek_ne_jezi_se.Client"""
import builtins
from copy import deepcopy

from clovek_ne_jezi_se.client import Client
from clovek_ne_jezi_se.agents import HumanPlayer
from clovek_ne_jezi_se.game_state import (
    MoveContainer, BoardSpace, EMPTY_SYMBOL
)


def monkey_roll(roll_value):
    """Monkeypatch for dice roll"""
    return roll_value


class TestClient:
    player_names = ['red', 'blue', 'green', 'yellow']
    players = [HumanPlayer(name=name) for name in player_names]

    client = Client(players=players)
    client.initialize()

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
        expected_client = deepcopy(self.client)

        # Set roll value to 6
        monkeypatch.setattr(played_client, 'roll', lambda: monkey_roll(6))
        # For HumanAgent choose_move input, always select 0th
        idx_move_input = 0
        monkeypatch.setattr(builtins, 'input', lambda x: idx_move_input)

        # Play one round with fixed (monkeypatched) dice and move choice
        for _ in range(len(played_client.players)):
            played_client.play()

        played_game_state = played_client.get_game_state()


        # Move 0th piece to main board from waiting for each player
        expected_game_state = expected_client.get_game_state()
        for player_name in expected_client._player_names:
            expected_game_state.do(MoveContainer(
                from_space=BoardSpace(
                    kind='waiting', idx=0, occupied_by=player_name,
                    allowed_occupants=[player_name, EMPTY_SYMBOL]
                ),
                to_space=BoardSpace(
                    kind='main',
                    idx=expected_game_state.get_main_entry_index(
                        player_name
                    ),
                    occupied_by=EMPTY_SYMBOL,
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
