'''Clovek ne jezi se game board and plays'''
EMPTY_VALUE = '-'


class Player:
    def __init__(self, agent, symbol):
        self.agent = agent
        self.symbol = self._set_symbol(symbol)
        self.home = 4 * (EMPTY_VALUE)

    def _set_symbol(self, symbol):
        if not isinstance(symbol, str):
            raise ValueError("Player symbol must be a string")
        
        return symbol


    def __repr__(self):
        return (
            'Player agent {}, game piece {}'
            .format(self.agent, self.symbol)
        )


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


class Board:
    def __init__(self, section_length, symbols=('1', '2', '3', '4')):
        self.section_length = section_length
        self.spaces = self._setup_spaces(EMPTY_VALUE)
        self.symbols = symbols
        self.homes = self._setup_homes()
      

    def _setup_spaces(self, EMPTY_VALUE):

        if self.section_length < 4:
            raise ValueError('Sections must have length 4 or greater')

        if self.section_length % 2 != 0:
            raise ValueError('Sections must have even length')
        
        return 4 * self.section_length * (EMPTY_VALUE)


    def _setup_homes(self):

        res = {}
        for symbol in self.symbols:
            res[symbol] = 4 * (EMPTY_VALUE)

        return res


    def _get_private_symbol(self, public_symbol):

        return self.symbols.index(public_symbol)

    def __repr__(self):
        if self.section_length == 4:
            res = ("\n" \
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

            for symbol in self.symbols:
                res += (
                "\nplayer {} home: {} | {} | {} | {} "
                .format(symbol, *(4 * (EMPTY_VALUE)))
            )
            return res

        else:
            raise NotImplementedError(
                'Board representation only for 16 space main board'
            )
    


class Game:
    def __init__(self, players):
        self.players = players
        self.board = Board(players.n_players, players.symbols)