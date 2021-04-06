"""Player classes"""
import abc
from typing import Sequence
import logging
from random import randint

import attr

import matplotlib.pyplot as plt
import numpy as np

from clovek_ne_jezi_se.game_state import GameState, MoveContainer
from clovek_ne_jezi_se.log_handler import handler


logger = logging.getLogger(__name__)
logger.addHandler(handler)


@attr.s
class Player:
    """
    Base class for all player agents

    Parameters
    ----------
    name :
        Player name, must be a string
    print_game_state :
        Whether or not to display graphical representation of game state.
        Use cases: set to False for unit tests, True for interactive play.


    """
    name = attr.ib(type=str, validator=attr.validators.instance_of(str))
    print_game_state = attr.ib(type=bool, default=False)

    def choose_move(
        self, game_state: 'GameState',
        allowed_moves: Sequence['MoveContainer']
    ) -> 'MoveContainer':
        """Choose among moves."""
        msg = 'Allowed moves with index:\n'

        for move_idx, move in enumerate(allowed_moves):
            msg += f'Index: {move_idx}, move: {move}\n'

        self.log(msg)
        chosen_move_idx = self.choose_move_idx(game_state, allowed_moves)
        res = allowed_moves[chosen_move_idx]
        self.log(f'Chose {res}')

        return res

    @abc.abstractmethod
    def choose_move_idx(
        self, game_state: 'GameState',
        allowed_moves: Sequence[Sequence['MoveContainer']]
    ) -> int:
        return

    def log(self, message):
        res = ':'.join([self.__repr__(), message])
        logger.debug(res)

    def draw(self, game_state: 'GameState', figsize=(8, 6)):
        """Delegate to GameState.draw() for interactive play"""
        game_state.draw(figsize=figsize)
        plt.show()


@attr.s
class HumanPlayer(Player):
    """Interactive human player"""
    print_game_state = attr.ib(default=True)

    def choose_move_idx(
        self, game_state: 'GameState',
        allowed_moves: Sequence['MoveContainer']
    ) -> int:
        res = int(input('Enter chosen move index: '))
        return res


@attr.s
class RandomPlayer(Player):
    """Player that selects uniformly randomly from allowed moves"""
    def choose_move_idx(
        self, game_state: 'GameState',
        allowed_moves: Sequence[Sequence['MoveContainer']]
    ) -> int:
        """TODO: Test me???"""
        idx = randint(0, len(allowed_moves)-1)
        return idx


@attr.s
class FurthestAlongPlayer(Player):
    def choose_move_idx(
        self, game_state: 'GameState',
        allowed_moves: Sequence[Sequence['MoveContainer']]
    ) -> int:
        """
        Return index for move that is closes to the player's last home space
        """
        player_from_moves = []
        for move_components in allowed_moves:
            for move_component in move_components:
                if move_component.from_space.occupied_by == self.name:
                    player_from_moves.append(move_component)

        player_from_spaces = [move.from_space for move in player_from_moves]

        distances_to_end = [
            game_state.distance_to_end(space) for space in player_from_spaces
        ]
        idx_furthest_along = np.argmin(distances_to_end)

        return idx_furthest_along
