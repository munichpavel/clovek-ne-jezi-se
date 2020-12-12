"""Tests for game classes"""
import pytest

import numpy as np

import networkx as nx

from clovek_ne_jezi_se.game import (
    GameState, BoardSpace, MoveContainer
)
from clovek_ne_jezi_se.consts import EMPTY_SYMBOL


def test_board_space_errors():
    with pytest.raises(ValueError):
        BoardSpace('yadda', 0, 'red', 'all')


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
    player_enter_main_indices = []
    for player_name in player_names:
        player_enter_main_indices.append(
            game_state.get_player_enter_main_index(player_name)
        )

    @pytest.mark.parametrize(
        'player_name,expected',
        [
            (player_names[0], player_enter_main_indices[0]),
            (player_names[1], player_enter_main_indices[1]),
            (player_names[2], player_enter_main_indices[2]),
            (player_names[3], player_enter_main_indices[3])
        ]
    )
    def test_get_player_enter_main_index(self, player_name, expected):
        assert self.game_state.get_player_enter_main_index(player_name) \
            == expected

    @pytest.mark.parametrize("idx", range(len(player_names) * section_length))
    def test_get_main_board_space(self, idx):
        assert self.game_state.get_board_space(kind='main', idx=idx) \
            == BoardSpace(
                kind='main', idx=idx, occupied_by=EMPTY_SYMBOL,
                allowed_occupants=self.player_names
            )

    @pytest.mark.parametrize(
        "kind,idx",
        [('yadda', 0), ('main', 42)]
    )
    def test_get_board_space_returns_none(self, kind, idx):
        assert self.game_state.get_board_space(kind=kind, idx=idx) is None

    @pytest.mark.parametrize("player_name", player_names)
    @pytest.mark.parametrize("idx", range(pieces_per_player))
    def test_get_waiting_space(self, player_name, idx):
        assert self.game_state.get_board_space(
            kind='waiting', idx=idx, player_name=player_name
            ) \
            == BoardSpace(
                kind='waiting', idx=idx, occupied_by=player_name,
                allowed_occupants=[player_name]
            )

    @pytest.mark.parametrize("player_name", player_names)
    @pytest.mark.parametrize("idx", range(pieces_per_player))
    def test_get_home_space(self, player_name, idx):
        assert self.game_state.get_board_space(
            kind='home', idx=idx, player_name=player_name
            ) \
            == BoardSpace(
                kind='home', idx=idx, occupied_by=EMPTY_SYMBOL,
                allowed_occupants=[player_name]
            )

    @pytest.mark.parametrize(
        "player_idx,from_kind,from_idx,roll,expected_to_space",
        [
      #      (0, 'waiting', 0, 8, None),
            (
                0, 'waiting', 0, 6,
                BoardSpace(
                    kind='main', idx=player_enter_main_indices[0],
                    occupied_by=EMPTY_SYMBOL, allowed_occupants=player_names
                )
            ),
        ]
    )
    def test_move_factory_initial_game_state(
        self, player_idx, from_kind, from_idx, roll, expected_to_space
    ):
        player_name = self.player_names[player_idx]
        from_space = self.game_state.get_board_space(
            kind=from_kind, idx=from_idx, player_name=player_name
        )

        res = self.game_state.move_factory(from_space, roll)
        if expected_to_space is None:
            assert res.to_space is None
        else:
            assert res == MoveContainer(
                from_space=from_space, to_space=expected_to_space
            )
