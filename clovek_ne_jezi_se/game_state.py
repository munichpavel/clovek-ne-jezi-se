"""Clovek ne jezi se game board and plays"""
from math import pi
from typing import Sequence, Union

import attr

import networkx as nx

import matplotlib.pyplot as plt

from .utils import (
    make_even_points_on_circle, make_dict_from_lists,
    GraphQueryParams, get_filtered_subgraph_view, get_filtered_node_names
)


EMPTY_SYMBOL = '-'


def is_positive(instance, attribute, value):
    """attr validator for positivity"""
    if value <= 0:
        raise ValueError(f'"value" must be positive, got {value}')


@attr.s
class GameState:
    """
    Game state including board, player pieces and query methods. The board
    consists of three areas: the waiting areas for each, the shared main board,
    and the home areas for each player.
    """
    player_names = attr.ib(type=Sequence)
    pieces_per_player = attr.ib(kw_only=True, type=int, default=4, validator=[
        attr.validators.instance_of(int),
        is_positive
    ])
    section_length = attr.ib(kw_only=True, type=int, default=10, validator=[
        attr.validators.instance_of(int),
        is_positive
    ])
    number_of_dice_faces = attr.ib(
        kw_only=True, type=int, default=6, validator=[
            attr.validators.instance_of(int),
            is_positive
        ]
    )
    empty_symbol = attr.ib(kw_only=True, default=EMPTY_SYMBOL)

    def initialize(self):
        """Create internal game-state representation"""
        self._main_board_length = len(self.player_names) * self.section_length
        self._graph = nx.DiGraph()
        self._create_main_graph()
        self._create_waiting_graphs()
        self._join_waiting_graphs_to_main()
        self._create_home_graphs()
        self._join_home_graphs_to_main()

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
            main_board_graph.nodes[node_name]['allowed_occupants'] = \
                self.player_names + [EMPTY_SYMBOL]

        # Annotation of edges
        for start_node, stop_node in main_board_graph.edges():
            main_board_graph[start_node][stop_node]['allowed_traversers'] \
                = self.player_names

        # Adjust annotation of main edges to ensure player enters home
        # after a circuit and does not loop around main board ad infinitum
        self._set_enter_main_node_names(main_board_graph)
        for player_name in self.player_names:
            enter_main_node_name = self._enter_main_node_names[player_name]

            prehome_node_name = next(
                main_board_graph.predecessors(enter_main_node_name)
            )
            other_player_names = [
                other_player_name for other_player_name in self.player_names
                if other_player_name != player_name
            ]
            main_board_graph[prehome_node_name][enter_main_node_name][
                'allowed_traversers'
            ] = other_player_names

        self._graph.update(main_board_graph)

    def _set_enter_main_node_names(self, main_board_graph):
        res = {}
        query_mains = GraphQueryParams(
            graph_component='node', query_type='equality',
            label='kind', value='main'
        )
        for player_name in self.player_names:

            enter_main_idx = self.get_main_entry_index(player_name)
            query_entry_idx = GraphQueryParams(
                graph_component='node', query_type='equality',
                label='idx', value=enter_main_idx
            )
            enter_main_node_name = get_filtered_node_names(
                main_board_graph, [query_mains, query_entry_idx]
            )[0]
            res[player_name] = enter_main_node_name

        self._enter_main_node_names = res

    def get_main_entry_index(self, player_name):
        """Get main board index where player enters from waiting."""
        player_order = self.player_names.index(player_name)
        return player_order * self.section_length

    def _create_waiting_graphs(self):

        for player_name in self.player_names:
            player_waiting_graph = nx.Graph()
            player_waiting_graph.add_nodes_from(
                [
                    (
                        f'w-{player_name}-{idx}',
                        dict(
                            kind='waiting', idx=idx, occupied_by=player_name,
                            allowed_occupants=[player_name, EMPTY_SYMBOL]
                        )
                    )
                    for idx in range(self.pieces_per_player)
                ],

            )
            # Add to main graph
            self._graph.update(player_waiting_graph)

    def _join_waiting_graphs_to_main(self):
        for player_name in self.player_names:
            query_waitings = GraphQueryParams(
                graph_component='node', query_type='equality',
                label='kind', value='waiting'
            )
            query_allowed_occupants = GraphQueryParams(
                graph_component='node', query_type='inclusion',
                label='allowed_occupants', value=player_name
            )

            waiting_node_names = get_filtered_node_names(
                self._graph, [query_waitings, query_allowed_occupants]
            )

            self._graph.add_edges_from(
                [
                    (node_name, self._enter_main_node_names[player_name])
                    for node_name in waiting_node_names
                ],
                allowed_traversers=[player_name]
            )

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

        # Annotate home graphs
        for player_name in self.player_names:
            player_home_graph = home_graphs[player_name]

            # Annotate nodes
            for idx, node_name in enumerate(player_home_graph.nodes()):
                player_home_graph.nodes[node_name]['idx'] = idx
                player_home_graph.nodes[node_name]['kind'] = 'home'
                player_home_graph.nodes[node_name]['occupied_by'] \
                    = EMPTY_SYMBOL
                player_home_graph.nodes[node_name]['allowed_occupants'] \
                    = [player_name, EMPTY_SYMBOL]

            # Annotate edges
            for edge in player_home_graph.edges:
                player_home_graph[edge[0]][edge[1]]['allowed_traversers'] \
                    = [player_name, EMPTY_SYMBOL]

            # Add to main graph
            self._graph.update(player_home_graph)

    def _join_home_graphs_to_main(self):
        for player_name in self.player_names:

            enter_main_node_name = self._enter_main_node_names[player_name]
            # TODO: Is this dangerous? Do I modify the graph in-place?
            prehome_node_name = next(
                self._graph.predecessors(enter_main_node_name)
            )

            first_home_space = self.get_board_space(
                kind='home', idx=0, player_name=player_name
            )
            first_home_space_name = self._get_board_space_node_name(
                first_home_space
            )

            self._graph.add_edge(
                prehome_node_name, first_home_space_name,
                allowed_traversers=[player_name]
            )

    # Query methods
    def get_board_space(
        self, kind: str, idx: int, player_name=None
    ) -> Union[None, 'BoardSpace']:
        """
        Get BoardSpace instance of given kind and index, with player_name
        required for waiting or home spaces.
        """
        board_space_query_paramses = self._get_board_space_query_paramses(
            kind, idx, player_name
        )
        space_subgraph = get_filtered_subgraph_view(
            self._graph, board_space_query_paramses
        )
        # TODO throw error if not space_subgraph.number_of_nodes() == 1 ?
        if space_subgraph.number_of_nodes() == 0:
            return None

        node_name = get_filtered_node_names(
            self._graph, board_space_query_paramses
        )[0]
        node_data = space_subgraph.nodes[node_name]
        return BoardSpace(**node_data)

    def _get_board_space_query_paramses(
        self, kind: str, idx: int, player_name: str
    ) -> Sequence['GraphQueryParams']:
        """Return list of GraphQueryParams's for get_board_space method."""
        kind_query = GraphQueryParams(
            graph_component='node', query_type='equality',
            label='kind', value=kind
        )
        kind_query.set_value_type()

        idx_query = GraphQueryParams(
            graph_component='node', query_type='equality',
            label='idx', value=idx
        )
        idx_query.set_value_type()

        query_paramses = [kind_query, idx_query]

        if player_name is not None:
            allowed_occupants_query = GraphQueryParams(
                graph_component='node', query_type='inclusion',
                label='allowed_occupants', value=player_name
            )
            allowed_occupants_query.set_value_type()
            query_paramses.append(allowed_occupants_query)

        return query_paramses

    def _get_board_space_node_name(self, board_space: 'BoardSpace') -> str:
        """Returns node name of input board space"""
        kind_query_params = GraphQueryParams(
            graph_component='node', query_type='equality',
            label='kind', value=board_space.kind
        )
        player_name_query_params = GraphQueryParams(
            graph_component='node', query_type='equality',
            label='allowed_occupants', value=board_space.allowed_occupants
        )
        idx_query_params = GraphQueryParams(
            graph_component='node', query_type='equality',
            label='idx', value=board_space.idx
        )

        node_names = get_filtered_node_names(
            self._graph,
            [kind_query_params, player_name_query_params, idx_query_params]
        )

        if len(node_names) != 1:
            raise ValueError(
                f'Board space {board_space} node name not well-defined'
            )
        else:
            return node_names[0]

    # Moves
    def do(self, move_container: 'MoveContainer'):
        '''
        Update game state according to move_container; assumes move_container
        is valid
        '''
        from_node_name = self._get_board_space_node_name(
            move_container.from_space
        )
        from_node = self._graph.nodes[from_node_name]
        from_node['occupied_by'] = EMPTY_SYMBOL

        to_node_name = self._get_board_space_node_name(
            move_container.to_space
        )
        to_node = self._graph.nodes[to_node_name]
        to_node['occupied_by'] = move_container.from_space.occupied_by

    def get_player_moves(
        self, roll: int, player_name: str
    ) -> Sequence:
        """
        Generate a list of valid moves for all pieces of a given player name
        and roll, potentially including secondary moves like sending an
        opponent's piece back to its waiting area.
        """
        player_occupied_query_paramses = [GraphQueryParams(
            graph_component='node', query_type='equality', label='occupied_by',
            value=player_name
        )]
        player_occupied_node_names = get_filtered_node_names(
            self._graph, player_occupied_query_paramses
        )
        primary_moves = self._get_primary_moves(
            roll, player_occupied_node_names
        )

        # Add any secondary moves triggered by primary moves
        all_moves = []
        for primary_move in primary_moves:
            piece_moves = []
            piece_moves.append(primary_move)
            if primary_move.to_space.occupied_by != EMPTY_SYMBOL:
                secondary_move = self._get_secondary_move(primary_move)
                piece_moves.append(secondary_move)
            all_moves.append(piece_moves)
        return all_moves

    def _get_primary_moves(
        self, roll: int, node_names: Sequence[str]
    ) -> Sequence['MoveContainer']:
        """
        Generate list of valid primary board moves, meaning only the move
        from the input node_names and roll, excluding moves caused by the
        primary one, like sending a piece back to its waiting area.
        """
        primary_moves = []
        for node_name in node_names:
            node = self._graph.nodes[node_name]
            board_space = self.get_board_space(
                kind=node['kind'], idx=node['idx'],
                player_name=node['occupied_by']
            )
            primary_move_candidate = self.move_factory(
                from_space=board_space, roll=roll
            )
            if primary_move_candidate.to_space is not None:
                primary_moves.append(primary_move_candidate)

        return primary_moves

    def _get_secondary_move(
        self, primary_move: 'MoveContainer'
    ) -> 'MoveContainer':
        """Get secondary moved triggered by primary move"""
        waiting_spaces = [
            self.get_board_space(
                'waiting', idx,
                player_name=primary_move.to_space.occupied_by
            ) for idx in range(self.pieces_per_player)
        ]
        empty_waiting_idxs = [
            waiting_space.idx for waiting_space in waiting_spaces
            if waiting_space.occupied_by == EMPTY_SYMBOL
        ]
        # Pick first empty waiting space
        send_to_waiting_idx = empty_waiting_idxs[0]
        secondary_move = MoveContainer(
            from_space=primary_move.to_space,
            to_space=BoardSpace(
                kind='waiting', idx=send_to_waiting_idx,
                occupied_by=EMPTY_SYMBOL,
                allowed_occupants=[
                    primary_move.to_space.occupied_by,
                    EMPTY_SYMBOL
                ]
            )
        )

        return secondary_move

    def move_factory(
        self, from_space: 'BoardSpace', roll: int
    ) -> 'MoveContainer':
        """
        Return either MoveContainer for given BoardSpace start ('from') and
        roll. No validity check is made on the from_space.
        """

        to_space = self._get_to_space(from_space, roll)
        return MoveContainer(
            from_space=from_space,
            to_space=to_space
        )

    def _get_to_space(
        self, from_space: 'BoardSpace', roll: int
    ) -> Union['BoardSpace', None]:
        """
        For a given start (from_space) and roll, returns either a valid end
        position (to_space) or None if the move is invalid
        """
        if from_space.kind == 'waiting':
            to_node_name = self._enter_main_node_names[from_space.occupied_by]
            to_node = self._graph.nodes[to_node_name]
            if (
                roll != self.number_of_dice_faces or
                to_node['occupied_by'] == from_space.occupied_by
            ):
                return None
            else:
                return BoardSpace(
                    kind=to_node['kind'],
                    idx=to_node['idx'],
                    occupied_by=to_node['occupied_by'],
                    allowed_occupants=to_node['allowed_occupants']
                )

        player_subgraph_query_paramses = \
            self._get_player_subgraph_query_paramses(from_space.occupied_by)

        player_subgraph_view = get_filtered_subgraph_view(
            self._graph, player_subgraph_query_paramses
        )
        from_node_name = self._get_board_space_node_name(from_space)

        advance_edges = list(nx.dfs_edges(
            player_subgraph_view, source=from_node_name, depth_limit=roll+1
        ))
        to_node_name = advance_edges[roll-1][1]
        to_node = self._graph.nodes[to_node_name]
        to_space = BoardSpace(
            kind=to_node['kind'],
            idx=to_node['idx'],
            occupied_by=to_node['occupied_by'],
            allowed_occupants=to_node['allowed_occupants']
        )

        return to_space

    def _get_player_subgraph_query_paramses(
        self, player_name: str
    ) -> Sequence['GraphQueryParams']:
        """Return graph query paramter list"""
        allowed_traversers_query_params = GraphQueryParams(
          graph_component='edge', query_type='inclusion',
          label='allowed_traversers', value=player_name
        )
        allowed_occupants_query_params = GraphQueryParams(
            graph_component='node', query_type='inclusion',
            label='allowed_occupants', value=player_name
        )
        return [
            allowed_traversers_query_params, allowed_occupants_query_params
        ]

    # Visualization
    def draw(self, figsize=(12, 8)):
        """Show game state graph with human-readable coordinates."""
        pos = self._get_graph_positions()

        plt.figure(figsize=figsize)
        nx.draw(self._graph, pos, with_labels=True)

    def _get_graph_positions(self):
        start_radians = -pi/2 - 2 * pi / self._main_board_length
        main_radius = 2
        main_center = (0, 0)

        pos = {}
        query_main = GraphQueryParams(
            graph_component='node', query_type='equality',
            label='kind', value='main'
        )
        query_main.set_value_type()
        main_node_names = get_filtered_node_names(self._graph, [query_main])

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

        query_waiting = GraphQueryParams(
                graph_component='node', query_type='equality',
                label='kind', value='waiting'
            )
        query_waiting.set_value_type()
        for idx, player_name in enumerate(self.player_names):

            query_allowed_occupants = GraphQueryParams(
                graph_component='node', query_type='inclusion',
                label='allowed_occupants', value=player_name
            )
            query_allowed_occupants.set_value_type()
            player_waiting_node_names = get_filtered_node_names(
                self._graph, [query_waiting, query_allowed_occupants]
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
        query_home = GraphQueryParams(
            graph_component='node', query_type='equality',
            label='kind', value='home'
        )
        query_home.set_value_type()
        for home_order in range(self.pieces_per_player):
            query_home_order = GraphQueryParams(
                graph_component='node', query_type='equality',
                label='idx', value=home_order
            )
            query_home_order.set_value_type()
            player_home_node_names = get_filtered_node_names(
                self._graph, [query_home, query_home_order]
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
    """Container for board spaces."""
    kind = attr.ib(
        type=str,
        validator=attr.validators.in_(['waiting', 'main', 'home'])
    )
    idx = attr.ib(type=int)
    occupied_by = attr.ib(type=str, default=EMPTY_SYMBOL)
    allowed_occupants = attr.ib(type=Sequence, default=[])


@attr.s
class MoveContainer:
    """Container for board moves."""
    from_space = attr.ib(type=BoardSpace)
    to_space = attr.ib(type=BoardSpace)
