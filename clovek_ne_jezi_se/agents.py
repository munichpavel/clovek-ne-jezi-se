"""Player classes"""
import abc
from typing import Sequence

import attr

from clovek_ne_jezi_se.game_state import GameState, MoveContainer


@attr.s
class Player:
    """Base class for all player agents"""
    name = attr.ib(validator=attr.validators.instance_of(str))

    @abc.abstractmethod
    def choose_move(
        self, game_state: 'GameState',
        allowed_moves: Sequence['MoveContainer']
    ) -> 'MoveContainer':
        """Choose among moves."""
        return

    @abc.abstractclassmethod
    def get_waiting_area_representation(
        self, game_state: 'GameState'
    ) -> dict:
        """Representation the state of the waiting areas."""
        return

    @abc.abstractclassmethod
    def get_main_spaces_representation(self, game_state: 'GameState') -> list:
        """Representation the state of the main board."""
        return

    @abc.abstractclassmethod
    def get_home_area_representation(
        self, game_state: 'GameState'
    ) -> dict:
        """Representation the state of the home areas."""
        return


class HumanPlayer(Player):
    def choose_move(
        self, game_state: 'GameState',
        allowed_moves: Sequence['MoveContainer']
    ) -> 'MoveContainer':
        print('Allowed moves with index:\n')
        for move_idx, move in enumerate(allowed_moves):
            print(f'Index: {move_idx}, move: {move}')

        chosen_move_idx = int(input('Enter chosen move index: '))
        res = allowed_moves[chosen_move_idx]
        print(f'\nYou selected move {res}')
        return res

    def get_main_spaces_representation(self, game_state: 'GameState') -> list:
        res = []
        for idx in range(
            game_state.section_length * len(game_state.player_names)
        ):
            main_space_dict = dict(
                kind='main', idx=idx
            )
            main_space = game_state.get_board_space(**main_space_dict)
            res.append(main_space.occupied_by)
        return res

    def get_waiting_area_representation(
        self, game_state: 'GameState'
    ) -> dict:
        return self._get_game_state_counts(game_state, 'waiting')

    def get_home_area_representation(
        self, game_state: 'GameState'
    ) -> dict:
        return self._get_game_state_counts(game_state, 'home')

    def _get_game_state_counts(
        self, game_state: 'GameState', kind: str
    ) -> dict:
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

