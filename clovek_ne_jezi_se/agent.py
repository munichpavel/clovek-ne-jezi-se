from random import randint

from .consts import EMPTY_VALUE

class Player:
    
    def __init__(self, symbol):
     #   self.agent = agent
        self.symbol = self._set_symbol(symbol)
        self.home = 4 * (EMPTY_VALUE)


    def _set_symbol(self, symbol):
        if not isinstance(symbol, str):
            raise ValueError("Player symbol must be a string")
        
        return symbol


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

    


class FurthestAlongAgent(Player):
    '''Agent who always moves the game piece furthest along'''
    
    def take_action(self, board):

        return {'main': 3}

    def _find_furthest_along_position(self, board_component):
        return len(board_component) - board_component[::-1](self.symbol) - 1


class Players:
    def __init__(self, players):
        self.n_players = len(players)
        self._set_players(players)
        

    def _set_players(self, players):
        res = []
        for player in players:
            res.append(player.symbol)

        if len(set(res)) < len(players):
            raise ValueError('Player symbols must be unique')
        
        self.symbols = res

    
