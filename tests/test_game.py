"""Tests for game classes"""
import pytest

import numpy as np

import networkx as nx

from clovek_ne_jezi_se.game import (
    GameState, BoardSpace, MoveContainer
)

from clovek_ne_jezi_se.utils import (
    make_even_points_on_circle, make_dict_from_lists
)

from clovek_ne_jezi_se.consts import EMPTY_SYMBOL


class TestGameState:
    player_names = ['red', 'blue', 'green', 'yellow']
    pieces_per_player = 4
    section_length = 4
    game_state = GameState(
        player_names=player_names, pieces_per_player=pieces_per_player,
        section_length=section_length
    )
    game_state.initialize()

    # Set further variables for test cases
    player_waiting_to_main_indices = []
    for player_name in player_names:
        player_waiting_to_main_indices.append(
            game_state.get_player_waiting_to_main_index(player_name)
        )

    @pytest.mark.parametrize(
        'player_name,expected',
        [
            (player_names[0], player_waiting_to_main_indices[0]),
            (player_names[1], player_waiting_to_main_indices[1]),
            (player_names[2], player_waiting_to_main_indices[2]),
            (player_names[3], player_waiting_to_main_indices[3])
        ]
    )
    def test_get_player_waiting_to_main_index(self, player_name, expected):
        assert self.game_state.get_player_waiting_to_main_index(player_name) \
            == expected

    @pytest.mark.parametrize("idx", range(len(player_names) * section_length))
    def test_get_main_board_space(self, idx):
        assert self.game_state.get_board_space(kind='main', idx=idx) \
            == BoardSpace(
                kind='main', idx=idx, occupied_by=EMPTY_SYMBOL,
                allowed_occupants='all'
            )

    @pytest.mark.parametrize(
        "kind,idx",
        [('yadda', 0), ('main', 42), ('main', range(3))]
    )
    def test_get_board_space_returns_none(self, kind, idx):
        assert self.game_state.get_board_space(kind=kind, idx=idx) is None

    @pytest.mark.parametrize("player_name", player_names)
    @pytest.mark.parametrize("idx", range(pieces_per_player))
    def test_get_waiting_space(self, player_name, idx):
        assert self.game_state.get_board_space(
            kind='waiting', idx=idx, allowed_occupants=player_name
            ) \
            == BoardSpace(
                kind='waiting', idx=idx, occupied_by=player_name,
                allowed_occupants=player_name
            )

    @pytest.mark.parametrize("player_name", player_names)
    @pytest.mark.parametrize("idx", range(pieces_per_player))
    def test_get_home_space(self, player_name, idx):
        assert self.game_state.get_board_space(
            kind='home', idx=idx, allowed_occupants=player_name
            ) \
            == BoardSpace(
                kind='home', idx=idx, occupied_by=EMPTY_SYMBOL,
                allowed_occupants=player_name
            )

    # def test_move_factory(self):
    #     player_idx = 0
    #     player_name = self.player_names[player_idx]
    #     roll = 6
    #     from_space = self.game_state.get_board_space(
    #         kind='waiting', idx=0, allowed_occupants=player_name
    #     )

    #     assert self.game_state.move_factory(from_space, roll) \
    #         == MoveContainer(
    #             from_space=BoardSpace(
    #                 kind='waiting', idx=0,
    #                 occupied_by=player_name, allowed_occupants=player_name
    #             ),
    #             to_space=BoardSpace(
    #                 kind='main',
    #                 idx=self.player_waiting_to_main_indices[player_idx],
    #                 occupied_by=EMPTY_SYMBOL, allowed_occupants='all')
    #         )
