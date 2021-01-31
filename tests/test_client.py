"""Tests for clovek_ne_jezi_se.Client"""
import builtins
from copy import deepcopy

from clovek_ne_jezi_se.client import Client
from clovek_ne_jezi_se.agents import HumanPlayer
from clovek_ne_jezi_se.game_state import (
    MoveContainer, BoardSpace, EMPTY_SYMBOL
)


class TestClient:
    player_names = ['red', 'blue', 'green', 'yellow']
    players = [
        HumanPlayer(name=name, print_game_state=False) for name in player_names
    ]

    client = Client(players=players)
    client.initialize()

    def test_next_player(self):
        player_round = [
            self.client.next_player() for _ in range(len(self.player_names))
        ]

        assert player_round == self.players

    def test_one_round_of_play(self, mocker, monkeypatch):
        played_client = deepcopy(self.client)
        expected_client = deepcopy(self.client)

        # Set roll values to 6 then 1 for each player turn
        mocker.patch.object(
            played_client, 'roll', side_effect=4 * [6, 1]
        )
        # For HumanAgent choose_move input, always select 0th
        idx_move_input = 0
        monkeypatch.setattr(builtins, 'input', lambda x: idx_move_input)

        # Play one round with fixed (monkeypatched) dice and move choice
        for _ in range(len(played_client.players)):
            played_client.take_turn()

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
                    ) + 1,
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

    def test_send_player_home(self, monkeypatch):
        played_client = deepcopy(self.client)
        expected_client = deepcopy(self.client)

        # Move red player to main 0, yellow to main 1
        played_game_state = played_client.get_game_state()
        played_game_state.do(MoveContainer(
            from_space=BoardSpace(
                kind='waiting', idx=0,
                occupied_by='red',
                allowed_occupants=['red', EMPTY_SYMBOL]
            ),
            to_space=BoardSpace(
                kind='main', idx=0,
                occupied_by=EMPTY_SYMBOL,
                allowed_occupants=self.player_names + [EMPTY_SYMBOL]
            )
        ))
        played_game_state.do(MoveContainer(
            from_space=BoardSpace(
                kind='waiting', idx=0,
                occupied_by='yellow',
                allowed_occupants=['yellow', EMPTY_SYMBOL]
            ),
            to_space=BoardSpace(
                kind='main', idx=1,
                occupied_by=EMPTY_SYMBOL,
                allowed_occupants=self.player_names + [EMPTY_SYMBOL]
            )
        ))

        # Set roll value to 1
        monkeypatch.setattr(played_client, 'roll', lambda: 1)
        # For HumanAgent choose_move input, always select 0th
        idx_move_input = 0
        monkeypatch.setattr(builtins, 'input', lambda x: idx_move_input)

        # Play once (red) with fixed (monkeypatched) dice and move choice
        played_client.take_turn()

        expected_game_state = expected_client.get_game_state()

        # Expect red to be at main index 1, all yellow back in waiting
        expected_game_state.do(MoveContainer(
            from_space=BoardSpace(
                kind='waiting', idx=0, occupied_by='red',
                allowed_occupants=['red', EMPTY_SYMBOL]
            ),
            to_space=BoardSpace(
                kind='main', idx=1,
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

    def test_play_finished(self, monkeypatch):

        played_client = deepcopy(self.client)
        played_game_state = played_client.get_game_state()

        idx_winner = 0
        winner_name = played_game_state.player_names[idx_winner]

        # move all pieces but first to home
        for idx in range(1, played_game_state.pieces_per_player):
            played_game_state.do(MoveContainer(
                from_space=BoardSpace(
                    kind='waiting', idx=idx,
                    occupied_by=winner_name,
                    allowed_occupants=[winner_name, EMPTY_SYMBOL]
                ),
                to_space=BoardSpace(
                    kind='home', idx=idx,
                    occupied_by=EMPTY_SYMBOL,
                    allowed_occupants=[winner_name, EMPTY_SYMBOL]
                )
            ))

        # Move first piece to one before home
        winner_enter_main_idx = played_game_state\
            .get_main_entry_index(winner_name)
        n_players = len(played_client.players)
        winner_prehome_idx = (winner_enter_main_idx - 1) % \
            played_client.main_board_section_length * n_players

        print(winner_prehome_idx)
        played_game_state.do(MoveContainer(
                from_space=BoardSpace(
                    kind='waiting', idx=0,
                    occupied_by=winner_name,
                    allowed_occupants=[winner_name, EMPTY_SYMBOL]
                ),
                to_space=BoardSpace(
                    kind='main', idx=winner_prehome_idx,
                    occupied_by=EMPTY_SYMBOL,
                    allowed_occupants=self.player_names + [EMPTY_SYMBOL]
                )
            ))

        monkeypatch.setattr(played_client, 'roll', lambda: 1)
        # Only one move possible, advance 1 to last open home spot
        monkeypatch.setattr(builtins, 'input', lambda x: 0)

        winner, _ = played_client.play()
        assert winner == played_client.players[idx_winner]
