from random import randint
import attr

from .consts import EMPTY_VALUE, NR_OF_DICE_FACES


@attr.s
class Player:
    symbol = attr.ib(validator=attr.validators.instance_of(str))
    number_of_players = attr.ib(validator=attr.validators.instance_of(int))

    def initialize_home(self):
        self.home = self.number_of_players * (EMPTY_VALUE)

    def _set_symbol(self, symbol):
        if not isinstance(symbol, str):
            raise ValueError("Player symbol must be a string")

        return symbol

    def set_order(self, order):
        self.order = order

    def set_start(self, order, section_length):
        self._start = order * section_length

    def get_start(self):
        return self._start

    def set_prehome_position(self, order, section_length):
        res = (
            (order * section_length - 1)
            % (section_length * self.number_of_players)
        )
        self._prehome_position = res

    def get_prehome_position(self):
        return self._prehome_position

    def roll(self):
        res = Player._get_roll_value()
        if Player.roll_is_valid(res):
            print("Player {} rolls a {}".format(self.symbol, res))
            return res
        else:
            raise ValueError('Roll value must be between 1 and 6')

    @staticmethod
    def _get_roll_value():
        return randint(1, NR_OF_DICE_FACES)

    @staticmethod
    def roll_is_valid(roll_value):
        return 1 <= roll_value <= NR_OF_DICE_FACES


class FurthestAlongAgent(Player):
    """Agent who always moves the game piece furthest along"""

    def take_action(self, board):
        roll_value = self.roll()

        if self.symbol in board.homes[self.symbol] and \
            self.action_is_valid(
                board.homes[self.symbol],
                self._find_furthest_along_position(board.homes[self.symbol])
                + roll_value
                ):
            ix = self._find_furthest_along_position(board.homes[self.symbol])
            return {'home': (ix, ix + roll_value)}

        elif self.symbol in board.spaces and \
            self.action_is_valid(
                board.spaces,
                self._find_furthest_along_position(board.spaces) + roll_value
                ):
            ix = self._find_furthest_along_position(board.spaces)
            return {'main': (ix, ix + roll_value)}

        else:
            return {}

    def _find_furthest_along_position(self, board_component):
        return (
            len(board_component)
            - board_component[::-1].index(self.symbol) - 1
        )
