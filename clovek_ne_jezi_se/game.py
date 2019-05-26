'''Clovek ne jezi se game board and plays'''


class Player:
    def __init__(self, agent, symbol):
        self.agent = agent
        self.symbol = symbol

    def __repr__(self):
        return (
            'Player agent {}, game piece {}'
            .format(self.agent, self.symbol)
        )



class Players:
    def __init__(self, players):
        self.symbols = self._set_players(players)

    def _set_players(self, players):
        res = []
        for player in players:
            res.append(player.symbol)

        if len(set(res)) < len(players):
            raise ValueError('Player symbols must be unique')
        
        return res


class Board:
    def __init__(self, section_length, empty_value='-'):
        self.section_length = section_length
        self.spaces = self.setup_spaces(empty_value)
      

    def setup_spaces(self, empty_value):

        if self.section_length < 4:
            raise ValueError('Sections must have length 4 or greater')

        if self.section_length % 2 != 0:
            raise ValueError('Sections must have even length')
        
        return 4 * self.section_length * (empty_value)


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
        