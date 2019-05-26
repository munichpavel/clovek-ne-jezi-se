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
            raise ValueError('Sections must have length 4 or greater')

        if self.section_length % 2 != 0:
            raise ValueError('Sections must have even length')
        
        return 4 * self.section_length * [BoardValues.EMPTY.value]


    def __repr__(self):
        if self.section_length == 4:
            return ( "\n" \
                "    -------------\n" \
                "    | {0} | {1} | {2} |\n" \
                "----------------------\n" \
                "| {14} | {15} |    | {3} | {4} |\n"    \
                "--------      -------|\n" \
                "| {13} |            | {5} |\n"    \
                "--------      -------|\n" \
                "| {12} | {11} |    | {7} | {6} |\n"    \
                "----------------------\n" \
                "    | {10} | {9} | {8} |\n" \
                "    -------------"
            ).format(*self.spaces)
        