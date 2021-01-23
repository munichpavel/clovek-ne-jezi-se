"""Player classes"""
import abc
from typing import Sequence
import logging
from random import randint

import attr

import matplotlib.pyplot as plt

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
        log_msg = 'Player ' + self.name + ' allowed moves with index:\n'

        for move_idx, move in enumerate(allowed_moves):
            log_msg += f'Index: {move_idx}, move: {move}\n'

        logger.info(log_msg)
        chosen_move_idx = self.choose_move_idx(game_state, allowed_moves)
        res = allowed_moves[chosen_move_idx]
        logger.info('Player ' + self.name + f' chose {res}')

        return res

    @abc.abstractmethod
    def choose_move_idx(
        self, game_state: 'GameState',
        allowed_moves: Sequence['MoveContainer']
    ) -> int:
        return


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

    def draw(self, game_state: 'GameState', figsize=(8, 6)):
        """Delegate to GameState.draw() for interactive play"""
        game_state.draw(figsize=figsize)
        plt.show()
