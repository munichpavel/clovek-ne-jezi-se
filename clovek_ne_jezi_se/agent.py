"""Player classes"""
import abc
from typing import Sequence

import attr

from clovek_ne_jezi_se.game_state import GameState, MoveContainer


@attr.s
class Player:
    name = attr.ib(validator=attr.validators.instance_of(str))

    @abc.abstractmethod
    def choose_move(
        self, game_state: 'GameState',
        allowed_moves: Sequence['MoveContainer']
    ):
        return


class HumanPlayer(Player):
    # TODO: Are type hints inherited in Sphinx from base method???
    def choose_move(self, game_state, allowed_moves):
        print('Allowed moves with index:\n')
        for move_idx, move in enumerate(allowed_moves):
            print(f'Index: {move_idx}, move: {move}')

        chosen_move_idx = int(input('Enter chosen move index: '))
        res = allowed_moves[chosen_move_idx]
        print(f'You selected move {res}')
        return res
