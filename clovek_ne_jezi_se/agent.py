from random import randint

from .consts import EMPTY_VALUE

class Player:
    
    def __init__(self, symbol):
        self.symbol = self._set_symbol(symbol)
        self.home = 4 * (EMPTY_VALUE)
        # Set within Players
        self.order = None
        # Set within Game
        self._start_position = None
        self._prehome_position = None


    def _set_symbol(self, symbol):
        if not isinstance(symbol, str):
            raise ValueError("Player symbol must be a string")
        
        return symbol


    def set_order(self, order):
        self.order = order

    
    def set_start_position(self, order, section_length):
        self._start_poistion = order * section_length


    def set_prehome_position(self, order, section_length):
        self._prehome_position = (4 - order) * section_length - 1


    def __repr__(self):
        return (
            'Player game piece {}'
            .format(self.symbol)
        )

    
    @staticmethod
    def roll():
        res = Player._get_roll_value()
        if Player._roll_is_valid(res):
            return res
        else:
            raise ValueError('Roll value must be between 1 and 6')


    @staticmethod
    def _get_roll_value():
        return randint(1,6)


    @staticmethod
    def _roll_is_valid(roll_value):
        return 1 <= roll_value <= 6

    
    @staticmethod
    def _action_is_valid(board_component, ix):
        if ix < 0 or ix > len(board_component) - 1:
            return False
        else:
            return board_component[ix] == EMPTY_VALUE


class FurthestAlongAgent(Player):
    '''Agent who always moves the game piece furthest along'''
    
    def take_action(self, board):
        roll_value = self.roll()
        
        if self.symbol in board.homes[self.symbol] and \
            self._action_is_valid(
                board.homes[self.symbol],
                self._find_furthest_along_position(board.homes[self.symbol]) + roll_value
            ):
            ix = self._find_furthest_along_position(board.homes[self.symbol])
            return {'home': (ix, ix + roll_value)}
            
        elif self.symbol in board.spaces and \
            self._action_is_valid(
                board.spaces,
                self._find_furthest_along_position(board.spaces) + roll_value
            ):
            ix = self._find_furthest_along_position(board.spaces)
            return {'main': (ix, ix + roll_value)}

        else:
            return {}

    def _find_furthest_along_position(self, board_component):
        return len(board_component) - board_component[::-1].index(self.symbol) - 1
        

class Players:
    def __init__(self, players):
        self.n_players = len(players)
        self._set_players(players)
        

    def _set_players(self, players):
        '''Set player orders, symbols and interface'''
        symbols = []
        self.players = {}
        for idx, player in enumerate(players):     
            player.set_order(idx)
            symbols.append(player.symbol)
            self.players[player.symbol] = player

        if len(set(symbols)) < len(players):
            raise ValueError('Player symbols must be unique')
        
        self.symbols = symbols

    
