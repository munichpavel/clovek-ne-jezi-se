"""Clovek ne jezi se game board and plays"""
from math import floor, pi
from random import randint
from typing import Sequence

import attr

import networkx as nx

import matplotlib.pyplot as plt

import numpy as np

from .consts import (
    EMPTY_SYMBOL, MINIMUM_SECTION_LENGTH, PIECES_PER_PLAYER, NR_OF_DICE_FACES,
    MOVE_KINDS
)

from .utils import (
    make_even_points_on_circle, make_dict_from_lists,
    get_node_filtered_subgraph
)


@attr.s
class GameState:
    """
    Game state including board and player pieces. The board consists of three
    areas: the waiting areas for each, the main board, and the home areas for
    each player.
    """
    # TODOs: add validators, like positivity, player symbols must be strings
    player_names = attr.ib(type=Sequence)
    pieces_per_player = attr.ib(type=int)
    section_length = attr.ib(type=int)

    def initialize(self):
        self._main_board_length = len(self.player_names) * self.section_length
        self._graph = nx.DiGraph()
        self._create_main_graph()
       # self._annotate_main_edges()
        self._create_waiting_graphs()
        self._join_waiting_graphs_to_main()
        self._create_home_graphs()
        #self._set_home_edges()

    def _create_main_graph(self):
        main_board_graph = nx.cycle_graph(
            [f'm{idx}' for idx in range(self._main_board_length)],
            create_using=nx.DiGraph
        )

        # Annotate nodes
        for idx, node_name in enumerate(main_board_graph.nodes()):
            main_board_graph.nodes[node_name]['idx'] = idx
            main_board_graph.nodes[node_name]['kind'] = 'main'
            main_board_graph.nodes[node_name]['occupied_by'] = EMPTY_SYMBOL
            main_board_graph.nodes[node_name]['allowed_occupants'] = 'all'

        for start_node, stop_node in main_board_graph.edges():
            main_board_graph[start_node][stop_node]['allowed_traversers'] \
                = self.player_names

        # for player_name in self.player_names:
        #     waiting_to_main_idx = self.get_player_waiting_to_main_index(
        #         player_name
        #     )
        #     waiting_to_main_node_name = self._get_query_node_names(
        #         dict(kind='main', idx=waiting_to_main_idx)
        #     )
        #     print(waiting_to_main_idx, waiting_to_main_node_name)

        #     pre_home_node_name = next(
        #         main_board_graph.predecessors(waiting_to_main_node_name)
        #     )
        #     main_board_graph[pre_home_node_name][waiting_to_main_node_name][
        #         'allowed_occupants'
        #     ].remove(player_name)

        self._graph.update(main_board_graph)

    def _create_waiting_graphs(self):

        for player_name in self.player_names:
            player_waiting_graph = nx.Graph()
            player_waiting_graph.add_nodes_from(
                [
                    (
                        f'w-{player_name}-{idx}',
                        dict(
                            kind='waiting', idx=idx, occupied_by=player_name,
                            allowed_occupants=player_name
                        )
                    )
                    for idx in range(self.pieces_per_player)
                ],

            )
            # Add to main graph
            self._graph.update(player_waiting_graph)

    def _join_waiting_graphs_to_main(self):
        for player_name in self.player_names:
            waiting_node_names = self._get_query_node_names(
                dict(kind='waiting', allowed_occupants=player_name)
            )
            main_board_entry_index = self.get_player_waiting_to_main_index(
                player_name
            )
            main_entry_node_name = self._get_query_node_names(
                dict(kind='main', idx=main_board_entry_index)
            )[0]
            edge_value_dict = dict(weight=6, allowed_traversers=[player_name])
            self._graph.add_edges_from(
                [
                    (node_name, main_entry_node_name)
                    for node_name in waiting_node_names
                ],
                **edge_value_dict
            )

    def get_player_waiting_to_main_index(self, player_name):
        player_order = self.player_names.index(player_name)
        return player_order * self.section_length

    def _get_query_node_names(self, query_dict: dict) -> list:
        nodes = get_node_filtered_subgraph(self._graph, query_dict)
        return list(nodes)

    def _create_home_graphs(self):
        home_graphs = {
                player_name: nx.path_graph(
                    [
                        f'h-{player_name}-{idx}'
                        for idx in range(self.pieces_per_player)
                    ],
                    create_using=nx.DiGraph
                )
                for player_name in self.player_names
            }

        for player_name in self.player_names:
            # Annotate
            player_home_graph = home_graphs[player_name]
            for idx, node_name in enumerate(player_home_graph.nodes()):
                player_home_graph.nodes[node_name]['idx'] = idx
                player_home_graph.nodes[node_name]['kind'] = 'home'
                player_home_graph.nodes[node_name]['occupied_by'] \
                    = EMPTY_SYMBOL
                player_home_graph.nodes[node_name]['allowed_occupants'] \
                    = player_name

            # Add to main graph
            self._graph.update(player_home_graph)

    def get_board_space(
        self, kind: str, idx: int, allowed_occupants='all'
    ) -> "BoardSpace":
        """Get BoardSpace instance of given kind and index"""
        space_subgraph = get_node_filtered_subgraph(
            self._graph,
            dict(kind=kind, idx=idx, allowed_occupants=allowed_occupants)
        )
        # TODO throw error if not space_subgraph.number_of_nodes() == 1 ?
        if space_subgraph.number_of_nodes() == 0:
            return None

        node_name = list(space_subgraph.nodes())[0]
        node_data = space_subgraph.nodes[node_name]
        return BoardSpace(**node_data)

    # Moves
    def move_factory(
        self, from_space: 'BoardSpace', roll: int
    ) -> 'MoveContainer':
        player_name = from_space.occupied_by
        to_space = BoardSpace(
            kind='main',
            idx=self.get_player_waiting_to_main_index(player_name),
            occupied_by=EMPTY_SYMBOL, allowed_occupants='all'
        )
        return MoveContainer(
            from_space=from_space,
            to_space=to_space
        )

    # Visualization
    def draw(self, figsize=(12, 8)):
        """Show game state graph with human-readable coordinates"""
        pos = self._get_graph_positions()

        plt.figure(figsize=figsize)
        nx.draw(self._graph, pos, with_labels=True)

    def _get_graph_positions(self):
        start_radians = -pi/2 - 2 * pi / self._main_board_length
        main_radius = 2
        main_center = (0, 0)

        pos = {}
        main_node_names = self._get_query_node_names(dict(kind='main'))
        main_coords = list(make_even_points_on_circle(
            center=main_center, radius=main_radius,
            n_points=self._main_board_length,
            start_radians=start_radians)
        )
        pos_main = make_dict_from_lists(main_node_names, main_coords)

        pos_players_waiting = {}
        player_waiting_centers = make_even_points_on_circle(
            center=main_center, radius=main_radius + 0.75,
            n_points=len(self.player_names), start_radians=start_radians
        )
        for idx, player_name in enumerate(self.player_names):
            player_waiting_node_names = self._get_query_node_names(
                dict(kind='waiting', allowed_occupants=player_name)
            )
            player_waiting_coords = list(make_even_points_on_circle(
                center=player_waiting_centers[idx], radius=0.5,
                n_points=self.pieces_per_player, start_radians=pi / 4
            ))
            pos_players_waiting = {
                **pos_players_waiting,
                **make_dict_from_lists(
                    player_waiting_node_names, player_waiting_coords
                )
            }

        pos_players_home = {}
        # Add home nodes in concentric rings inside main board
        for home_order in range(self.pieces_per_player):
            player_home_node_names = self._get_query_node_names(
                dict(kind='home', idx=home_order)
            )
            players_home_coords = make_even_points_on_circle(
                center=main_center,
                radius=main_radius - 0.4 * (home_order + 1),
                n_points=len(self.player_names),
                start_radians=-pi / 2
            )
            pos_players_home = {
                **pos_players_home,
                **make_dict_from_lists(
                    player_home_node_names, players_home_coords
                )
            }

        pos = {**pos, **pos_players_waiting, **pos_main, **pos_players_home}
        return pos


@attr.s
class BoardSpace:
    # TODO Add validators, e.g. kind in ['waiting', 'main', 'home']
    kind = attr.ib(type=str)
    idx = attr.ib(type=int)
    occupied_by = attr.ib(type=str, default=EMPTY_SYMBOL)
    allowed_occupants = attr.ib(type=str, default='all')


@attr.s
class MoveContainer:
    from_space = attr.ib(type=BoardSpace)
    to_space = attr.ib(type=BoardSpace)


class Board:
    """
    Game board representation, consisting of waiting area, main board,
    and home base representation. The internal representation of the game
    board is implemented in Game.

    The board state is represented by the main board and
    home base, while the waiting area is used only to determine
    allowable moves, e.g. if player A's waiting area has count 0,
    then she may not move a new symbol onto the main board.
    """
    def __init__(self, section_length, player_symbols=('1', '2', '3', '4')):
        self.section_length = section_length
        self.player_symbols = player_symbols

    def initialize(self):
        self.setup_spaces()
        self.setup_homes()
        self.setup_waiting_count()

    def setup_spaces(self):

        if self.section_length < MINIMUM_SECTION_LENGTH:
            raise ValueError(
                f'Sections must have length {MINIMUM_SECTION_LENGTH}'
                ' or greater'
            )

        if self.section_length % 2 != 0:
            raise ValueError('Sections must have even length')

        self.spaces = (
            len(self.player_symbols) * self.section_length * [EMPTY_SYMBOL]
        )

    def setup_homes(self):
        """Each player's home base consisting of 4 spots"""
        res = {}
        for symbol in self.player_symbols:
            res[symbol] = PIECES_PER_PLAYER * [EMPTY_SYMBOL]

        self.homes = res

    def setup_waiting_count(self):
        res = {}
        for symbol in self.player_symbols:
            res[symbol] = PIECES_PER_PLAYER

        self.waiting_count = res

    def get_private_symbol(self, public_symbol):
        if public_symbol == EMPTY_SYMBOL:
            return -1
        else:
            return self.player_symbols.index(public_symbol)

    def get_public_symbol(self, private_symbol):
        if private_symbol == -1:
            return EMPTY_SYMBOL
        else:
            return self.player_symbols[private_symbol]

    def __repr__(self):
        """Show board and players"""
        if self.section_length == 4:
            res = (
                "\n"
                "    -------------\n"
                "    | {6} | {7} | {8} |\n"
                "----------------------\n"
                "| {4} | {5} |    | {9} | {10} |\n"
                "--------      -------|\n"
                "| {3} |            | {11} |\n"
                "--------      -------|\n"
                "| {2} | {1} |    | {13} | {12} |\n"
                "----------------------\n"
                "    | {0} | {15} | {14} |\n"
                "    -------------"
            ).format(*self.spaces)

            for symbol in self.player_symbols:
                res += (
                    "\nplayer {} pieces in waiting area: {} "
                    .format(symbol, self.waiting_count[symbol])
                )
                res += (
                    "\nplayer {} home: {} | {} | {} | {}\n"
                    .format(symbol, *(self.homes[symbol]))
                )
            return res

        else:
            raise NotImplementedError(
                'Board representation only for 16 space main board'
            )


def check_start(self, attribute, value):
    # TODO: Refactor as in exapmple
    # https://www.attrs.org/en/stable/api.html#attr.validators.in_
    if value is not None and self.kind == 'leave_waiting':
        raise ValueError(
            'Leave home moves may not have a start position'
        )


@attr.s
class Move:
    """
    Container for game moves based on array (internal) board representation.
    """
    symbol = attr.ib()
    kinds = MOVE_KINDS
    kind = attr.ib()
    roll = attr.ib(kw_only=True, default=None)
    start = attr.ib(kw_only=True, default=None, validator=check_start)

    @kind.validator
    def check_kind(self, attribute, value):
        if value not in self.kinds:
            raise ValueError(f'Move kind must be a member of {self.kinds}')


@attr.s
class Game:
    players = attr.ib()
    section_length = attr.ib(default=4)

    def initialize(self):
        self.initialize_players()
        self.initialize_board()

    def initialize_players(self):
        self.n_players = len(self.players)
        self._validate_n_players()
        self._set_player_symbols()
        self._set_player_leave_waiting()
        self._set_player_prehome()

    def _validate_n_players(self):

        all_n_players = [player.number_of_players for player in self.players]

        if not len(set(all_n_players)) == 1:
            raise ValueError('Differing number of players entered')

        if not self.n_players == self.players[0].number_of_players:
            raise ValueError(
                f'{len(self.players)} players entered, '
                f'but should be {self.n_players}'
            )

    def _set_player_symbols(self):
        """Set player orders, symbols and interface"""
        symbols = []
        for idx, player in enumerate(self.players):
            player.set_order(idx)
            symbols.append(player.symbol)

        if len(set(symbols)) < self.n_players:
            raise ValueError('Player symbols must be unique')

        self.player_symbols = symbols

    def _set_player_leave_waiting(self):
        for idx, player in enumerate(self.players):
            player.set_leave_waiting_position(idx, self.section_length)

    def _set_player_prehome(self):
        for idx, player in enumerate(self.players):
            player.set_prehome_position(idx, self.section_length)

    def is_winner(self, symbol):
        return self.board.homes[symbol] == PIECES_PER_PLAYER * [symbol]

    def initialize_board(self):
        self.board = Board(self.section_length, self.player_symbols)
        self.board.initialize()
        # Initialize array representations
        self.initialize_waiting_count_array()
        self.initialize_spaces_array()
        self.initialize_homes_array()

    def get_player(self, symbol):
        idx = np.argmax(np.array(self.player_symbols) == symbol)
        return self.players[idx]

    # Board methods
    def initialize_waiting_count_array(self):
        res = [
            self.board.waiting_count.get(symbol)
            for symbol in self.player_symbols
        ]
        self._waiting_count = np.array(res)

    def get_waiting_count_array(self):
        return self._waiting_count

    def get_symbol_waiting_count(self, symbol):
        """
        Parameters
        ----------
        symbol : string

        Returns
        -------
         : int
            Symbol waiting count.
        """
        private_symbol = self.board.get_private_symbol(symbol)

        return self.get_waiting_count_array()[private_symbol]

    def set_symbol_waiting_count(self, symbol, count):
        """Set symbol waiting count value"""
        self.board.waiting_count[symbol] = count

        private_symbol = self.board.get_private_symbol(symbol)
        self._waiting_count[private_symbol] = count

    def initialize_spaces_array(self):
        """Initialize internal spaces representation"""
        res = [
            self.board.get_private_symbol(symbol)
            for symbol in self.board.spaces
        ]
        self._spaces_array = np.array(res)

    def get_spaces_array(self):
        return self._spaces_array

    def set_symbol_space_array(self, symbol, position):
        self.board.spaces[position] = symbol

        private_symbol = self.board.get_private_symbol(symbol)
        self._spaces_array[position] = private_symbol

    def initialize_homes_array(self):
        """Initialize internal homes representation"""
        res = []
        for symbol in self.player_symbols:
            res.append([
                self.board.get_private_symbol(symbol)
                for symbol in self.board.homes.get(symbol)
            ])

        self._homes_array = np.array(res)

    def get_homes_array(self):
        return self._homes_array

    def get_symbol_home_array(self, symbol):
        """
        Parameters
        ----------
        symbol : string

        Returns
        -------
         : np.array
            Symbol home array representation.
        """
        private_symbol = self.board.get_private_symbol(symbol)

        return self.get_homes_array()[private_symbol, :]

    def roll(self):
        """Roll dice method"""
        res = self._get_roll_value()
        if self.roll_is_valid(res):
            return res
        else:
            raise ValueError(f'Invalid roll value: {res}')

    def _get_roll_value(self):
        return randint(1, NR_OF_DICE_FACES)

    def roll_is_valid(self, value):
        return 1 <= value and value <= NR_OF_DICE_FACES

    # Game moves
    def get_moves_of(self, symbol, kind, roll):
        res = []
        starts = self.get_move_starts(symbol, kind)
        for start in starts:
            try:
                move = self.move_factory(symbol, kind, roll, start)
                res += move
            except ValueError:
                continue

        return res

    def get_move_starts(self, symbol, kind):
        """
        Get potential starting positions for symbol and move kind.
        No validation is performed.
        """
        if kind == 'leave_waiting':
            return self._get_leave_waiting_starts(symbol)
        elif kind == 'space_advance':
            return self._get_space_advance_starts(symbol)
        elif kind == 'space_to_home':
            return self._get_space_to_home_starts(symbol)
        elif kind == 'home_advance':
            return self._get_home_advance_starts(symbol)
        else:  # return_to_waiting
            return self._get_return_to_waiting_starts(symbol)

    def _get_leave_waiting_starts(self, symbol):
        return [None]

    def _get_space_advance_starts(self, symbol):
        return self.get_symbol_space_array(symbol)

    def _get_space_to_home_starts(self, symbol):
        return self.get_symbol_space_array(symbol)

    def _get_home_advance_starts(self, symbol):
        return self.get_symbol_home_positions(symbol)

    def _get_return_to_waiting_starts(self, symbol):
        """
        Returns [None] as return_to_waiting is an effect of another move
        and hence cannot be chosen directly by an agent, so no potential
        start positions returned.
        """
        return [None]

    def move_factory(self, symbol, kind, roll, start=None):
        """
        Create valid Move instances corresponding to input.

        Parameters
        ----------
        symbol : str
        kind : str
            One of consts.MOVE_KINDS
        roll : int
            Roll value
        start : int or None
            Start space or home position, None for moves involving the
            waiting area

        Returns
        -------
        res = list
            list of Move's
        """
        moves = self._get_moves(symbol, kind, roll, start)
        for move in moves:
            is_valid = self._get_validator(move.kind)
            if not is_valid(move):
                # TODO raise reasonable error--see #9.
                raise ValueError(f'Invalid move entered: {move}')

        return moves

    def _get_moves(self, symbol, kind, roll, start):
        res = []

        if kind == 'leave_waiting':
            res.append(Move(symbol, kind, roll=roll))

        else:
            res.append(Move(
                symbol, kind, roll=roll, start=start
            ))

        # Check if move sends other symbol piece back to its waiting area
        symbol_returned_to_waiting, position_returned_to_waiting = \
            self._get_returned_to_waiting_symbol_position(
                symbol, kind, roll, start
             )
        if symbol_returned_to_waiting is not None:
            res.append(Move(
                symbol_returned_to_waiting, 'return_to_waiting',
                start=position_returned_to_waiting
            ))

        return res

    def _get_returned_to_waiting_symbol_position(
        self, symbol, kind, roll, start
    ):
        """
        Returns tuple of symbol to be returned to waiting and its
        position before being returned
        """
        if kind == 'leave_waiting':
            position = self.get_player(symbol).get_leave_waiting_position()
        elif (
            kind == 'space_advance' and
            self._is_space_advance_move(symbol, roll, start)
        ):
            position = roll + start
        else:  # No other move kinds can send pieces back to waiting
            return (None, None)

        space_occupier = self.board.get_public_symbol(
            self.get_spaces_array()[position]
        )

        if space_occupier not in [EMPTY_SYMBOL, symbol]:
            return (space_occupier, position)
        else:
            return (None, None)

    def _get_validator(self, kind):
        if kind == 'leave_waiting':
            return self.leave_waiting_validator
        elif kind == 'space_advance':
            return self.space_advance_validator
        elif kind == 'space_to_home':
            return self.space_to_home_validator
        elif kind == 'home_advance':  # home_advance
            return self.home_advance_validator
        else:  # return_to_waiting
            return self.return_to_waiting_validator

    def leave_waiting_validator(self, move):
        """
        Parameters
        ----------
        move : Move

        Returns
        -------
        res : Boolean
        """
        return self._leave_waiting_is_valid(move.symbol, move.roll)

    def _leave_waiting_is_valid(self, symbol, roll):
        """
        Parameters
        ----------
        symbol : string
        roll : int

        Returns
        -------
         : Boolean
        """
        private_symbol = self.board.get_private_symbol(symbol)
        res = []
        # Check if a maximum rolled (usually 6)
        res.append(roll == NR_OF_DICE_FACES)

        # Check if still symbol pieces in waiting area
        if self._waiting_count[private_symbol] > 0:
            res.append(True)
        else:
            res.append(False)

        # Check if symbol's start position is occupied by own piece
        start = self.get_player(symbol).get_leave_waiting_position()
        occupied_by = self.get_space_occupier(start)
        res.append(occupied_by != symbol)

        return np.all(np.array(res))

    def get_space_occupier(self, position):
        """
        Get public symbol of occupier of board space position given, can be
        the empty symbol consts.EMPTY_SYMBOL

        Parameters
        ----------
        position : int
            Index of Game._spaces_array

        Returns
        -------
        res : str
            Member of Game.player_symbols or consts.EMPTY_SYMBOL
        """
        occupier_private_symbol = self.get_spaces_array()[position]
        return self.board.get_public_symbol(occupier_private_symbol)

    # Space advance move methods
    def space_advance_validator(self, move):
        if not self._is_space_advance_move(move.symbol, move.roll, move.start):
            return False

        start_occupied = self._space_start_occupied(move.symbol, move.start)
        end_occupied_by = self.get_spaces_array()[move.start + move.roll]

        end_blocked = move.symbol == end_occupied_by
        return start_occupied and not end_blocked

    def get_symbol_space_array(self, symbol):
        """
        Parameters
        ----------
        symbol : string
            Must be one of player symbols

        Returns
        -------
        symbol_positions : numpy.array
            1-d array of game board space indices where symbol has pieces
        """
        private_symbol = self.board.get_private_symbol(symbol)
        spaces_array = self.get_spaces_array()
        symbol_positions = np.where(spaces_array == private_symbol)[0]

        return symbol_positions

    def _is_space_advance_move(self, symbol, roll, start):
        """
        Determine if space advance move, sans validity checks.

        Parameters
        ----------
        symbol : string
        roll : int
        move_start : int

        Returns
        -------
         : Boolean
         """
        zeroed_position = self.get_zeroed_position(symbol, start)
        advance_ratio_of_spaces = (
            (zeroed_position + roll) / float(len(self._spaces_array))
        )

        after_prehome_ratio_rounded = floor(advance_ratio_of_spaces)

        res = not bool(after_prehome_ratio_rounded)
        return res

    def get_zeroed_position(self, symbol, position):
        """Calculate position relative to symbol leave waiting position"""
        leave_waiting = self.get_player(symbol).get_leave_waiting_position()
        res = (position - leave_waiting) % len(self._spaces_array)
        return res

    def _space_start_occupied(self, symbol, start):
        private_symbol = self.board.get_private_symbol(symbol)
        return self.get_spaces_array()[start] == private_symbol

    # Space to home move methods
    def space_to_home_validator(self, move):
        """
        Parameters
        ----------
        move : Move

        Returns
        -------
        res : Boolean
        """
        end = self.get_space_to_home_position(
            move.symbol, move.roll, move.start
        )
        if not self._position_within_home(end):
            # Return to avoid index error if end is beyond home spaces
            return False

        is_space_to_home = self._is_space_to_home_move(
            move.symbol, move.roll, move.start
        )
        end_not_occupied = self._home_position_unoccupied(move.symbol, end)

        return is_space_to_home and end_not_occupied

    def get_space_to_home_position(self, symbol, roll, start):
        """Get end position of space to home move, sans validity checks"""
        zeroed_start = self.get_zeroed_position(symbol, start)
        spaces_to_prehome = len(self._spaces_array) - zeroed_start

        return roll - spaces_to_prehome

    def _is_space_to_home_move(self, symbol, roll, start):
        """
        Determine if move is from (main) board space to home area,
        sans validity checks.

        Parameters
        ----------
        symbol : string
        position : int
        roll : int

        Returns
        -------
         : Boolean
        """
        return not self._is_space_advance_move(symbol, roll, start)

    def _home_position_unoccupied(self, symbol, position):
        return self.get_symbol_home_array(symbol)[position] == -1

    def _position_within_home(self, position):
        return position <= PIECES_PER_PLAYER - 1

    # Home advance move methods
    def home_advance_validator(self, move):
        """
        Parameters
        ----------
        move : Move

        Returns
        -------
        res : Boolean
        """
        return self._home_advance_is_valid(move.symbol, move.roll, move.start)

    def _home_advance_is_valid(self, symbol, roll, start):
        """
        A home advance is invalid if the end position is occupied
        or would land outside of the home spaces.

        Parameters
        ----------
        symbol : string
        roll : int
        start : int

        Returns
        -------
         : Boolean
        """
        end = start + roll

        if end > PIECES_PER_PLAYER - 1:
            return False

        symbol_home_positions = self.get_symbol_home_positions(symbol)

        return end not in symbol_home_positions

    def get_symbol_home_positions(self, symbol):
        """
        Parameters
        ----------
        symbol : string

        Returns
        -------
        symbol_positions : np.array
            Positions occupied by a symbol piece.
        """
        symbol_home_array = self.get_symbol_home_array(symbol)
        private_symbol = self.board.get_private_symbol(symbol)
        symbol_positions = np.where(symbol_home_array == private_symbol)[0]

        return symbol_positions

    # Return to waiting methods
    def return_to_waiting_validator(self, move):
        """
        Returns true, as return_to_waiting is generated within this class,
        as it is an effect of another agent move.

        Parameters
        ----------
        move : Move

        Returns
        -------
        res : Boolean
            Always returns True
        """
        return True

    # Do moves
    def do(self, symbol, kind, roll, start=None):
        """
        Try to create specified move, and update board if valid.
        """
        try:
            moves = self.move_factory(symbol, kind, roll=roll, start=start)
            for move in moves:
                update_with = self._get_updater(move.kind)
                update_with(move)
        except ValueError as err:
            print(err, '- board not updated')

    def _get_updater(self, move_kind):
        if move_kind == 'leave_waiting':
            return self._leave_waiting_updater
        elif move_kind == 'space_advance':
            return self._space_advance_updater
        elif move_kind == 'space_to_home':
            return self._space_to_home_updater
        elif move_kind == 'return_to_waiting':
            return self._return_to_waiting_updater
        else:
            raise NotImplementedError()

    def _leave_waiting_updater(self, move):
        current_count = self.get_symbol_waiting_count(move.symbol)
        self.set_symbol_waiting_count(move.symbol, current_count - 1)
        start = self.get_player(move.symbol).get_leave_waiting_position()
        self.set_symbol_space_array(move.symbol, start)

    def _space_advance_updater(self, move):
        self.set_symbol_space_array(EMPTY_SYMBOL, move.start)
        self.set_symbol_space_array(move.symbol, move.start + move.roll)

    def _space_to_home_updater(self, move):
        self.set_symbol_space_array(EMPTY_SYMBOL, move.start)
        end = self.get_space_to_home_position(
            move.symbol, move.roll, move.start
        )
        self.set_homes_array(move.symbol, end)

    def set_homes_array(self, symbol, position):
        self.board.homes[symbol][position] = symbol

        private_symbol = self.board.get_private_symbol(symbol)
        self._homes_array[private_symbol, position] = private_symbol

    def _return_to_waiting_updater(self, move):
        """
        Only update waiting counts, as the move causing return to waiting
        updates the spaces
        """
        pre_return_waiting_counts = self.get_symbol_waiting_count(move.symbol)
        self.set_symbol_waiting_count(
            move.symbol, pre_return_waiting_counts + 1
        )
