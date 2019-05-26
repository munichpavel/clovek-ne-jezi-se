'''Clovek ne jezi se game board and plays'''
from enum import Enum


class BoardValues(Enum):
    EMPTY = '-'
    PLAYER_1 = '1'
    PLAYER_2 = '2'
    PLAYER_3 = '3'
    PLAYER_4 = '4'



class Board:
    def __init__(self, section_length):
        self.section_length = section_length
        self.spaces = self.setup_spaces()
        
    
    def setup_spaces(self):
        if self.section_length < 4:
            raise ValueError('Sections must have lenght 4 or greater')

        if self.section_length % 2 != 0:
            raise ValueError('Sections must have even length')
        
        return 4 * self.section_length * [BoardValues.EMPTY]


    def __repr__(self):
        pass