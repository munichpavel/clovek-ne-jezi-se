"""Tests for clovek_ne_jezi_se.GameState"""
from copy import deepcopy

import pytest

from clovek_ne_jezi_se.game_state import (
    EMPTY_SYMBOL, GameState, BoardSpace, MoveContainer
)

from clovek_ne_jezi_se.utils import (
    GraphQueryParams,
    get_filtered_subgraph_view,
    get_filtered_node_names
)


def test_board_space_errors():
    with pytest.raises(ValueError):
        BoardSpace('yadda', 0, 'red', 'all')


class TestGameState:

    @pytest.mark.parametrize(
        'init_args_dict,Error',
        [
            (
                dict(
                    player_names=['red', 'blue', 'green', 'yellow'],
                    pieces_per_player=0
                ),
                ValueError
            ),
            (
                dict(
                    player_names=['red', 'blue', 'green', 'yellow'],
                    pieces_per_player=0.5
                ),
                TypeError
            ),
            (
                dict(
                    player_names=['red', 'blue', 'green', 'yellow'],
                    section_length=0
                ),
                ValueError
            ),
            (
                dict(
                    player_names=['red', 'blue', 'green', 'yellow'],
                    section_length=0.5
                ),
                TypeError
            ),
            (
                dict(
                    player_names=['red', 'blue', 'green', 'yellow'],
                    number_of_dice_faces=0
                ),
                ValueError
            ),
            (
                dict(
                    player_names=['red', 'blue', 'green', 'yellow'],
                    number_of_dice_faces=0.5
                ),
                TypeError
            ),
        ]
    )
    def test_game_state_initialization_errors(self, init_args_dict, Error):
        with pytest.raises(Error):
            game_state = GameState(**init_args_dict)
            game_state.initialize()

    # Set attributes for repeated use below
    player_names = ['red', 'blue', 'green', 'yellow']
    pieces_per_player = 4
    section_length = 4
    game_state = GameState(
        player_names=player_names, pieces_per_player=pieces_per_player,
        section_length=section_length
    )
    game_state.initialize()

    @pytest.mark.parametrize(
        'player_name,expected',
        [
            (player_names[0], 0),
            (player_names[1], 4),
            (player_names[2], 8),
            (player_names[3], 12)
        ]
    )
    def test_get_main_entry_index(self, player_name, expected):
        assert self.game_state.get_main_entry_index(player_name) \
            == expected

    # Set further variables for test cases
    player_enter_main_indices = {}
    for player_name in player_names:
        player_enter_main_indices[player_name] \
            = game_state.get_main_entry_index(player_name)

    # GameState setup tests
    @pytest.mark.parametrize("idx", range(len(player_names) * section_length))
    def test_get_main_board_space(self, idx):
        assert self.game_state.get_board_space(kind='main', idx=idx) \
            == BoardSpace(
                kind='main', idx=idx, occupied_by=EMPTY_SYMBOL,
                allowed_occupants=self.player_names + [EMPTY_SYMBOL]
            )

    @pytest.mark.parametrize(
        "kind,idx",
        [('yadda', 0), ('main', 42)]
    )
    def test_get_board_space_returns_none(self, kind, idx):
        assert self.game_state.get_board_space(kind=kind, idx=idx) is None

    @pytest.mark.parametrize("player_name", player_names)
    @pytest.mark.parametrize("idx", range(pieces_per_player))
    def test_get_waiting_space(self, player_name, idx):
        assert self.game_state.get_board_space(
            kind='waiting', idx=idx, player_name=player_name
            ) \
            == BoardSpace(
                kind='waiting', idx=idx, occupied_by=player_name,
                allowed_occupants=[player_name, EMPTY_SYMBOL]
            )

    @pytest.mark.parametrize("player_name", player_names)
    @pytest.mark.parametrize("idx", range(pieces_per_player))
    def test_get_home_space(self, player_name, idx):
        assert self.game_state.get_board_space(
            kind='home', idx=idx, player_name=player_name
            ) \
            == BoardSpace(
                kind='home', idx=idx, occupied_by=EMPTY_SYMBOL,
                allowed_occupants=[player_name, EMPTY_SYMBOL]
            )

    # For tests of moves from main to player home
    player_prehome_indices = {}
    for player_name in player_names:
        player_subgraph_paramses = [
            GraphQueryParams(
                graph_component='node', query_type='inclusion',
                label='allowed_occupants', value=player_name
            ),
            GraphQueryParams(
                graph_component='edge', query_type='inclusion',
                label='allowed_traversers', value=player_name
            )
        ]

        player_subgraph = get_filtered_subgraph_view(
            game_state._graph, player_subgraph_paramses
        )
        prehome_query_paramses = [
            GraphQueryParams(
                graph_component='node', query_type='equality',
                label='idx', value=0
            ),
            GraphQueryParams(
                graph_component='node', query_type='equality',
                label='kind', value='home'
            ),
        ]
        first_home_node_name = get_filtered_node_names(
            player_subgraph, prehome_query_paramses
        )[0]
        player_prehome_node_name = next(
            player_subgraph.predecessors(first_home_node_name)
        )
        player_prehome_indices[player_name] = \
            player_subgraph.nodes[player_prehome_node_name]['idx']

    @pytest.mark.parametrize(
        "roll,from_space,expected_to_space_kwargs",
        [
            (
                5, BoardSpace(
                    kind='waiting', idx=0, occupied_by='red',
                    allowed_occupants=['red', EMPTY_SYMBOL]
                ),
                None
            ),
            (
                6, BoardSpace(
                    kind='waiting', idx=0, occupied_by='red',
                    allowed_occupants=['red', EMPTY_SYMBOL]
                ),
                dict(
                    kind='main', idx=player_enter_main_indices['red'],
                    occupied_by=EMPTY_SYMBOL,
                    allowed_occupants=player_names + [EMPTY_SYMBOL]
                )
            ),
            (
                1, BoardSpace(
                    kind='main', idx=0, occupied_by='red',
                    allowed_occupants=player_names + [EMPTY_SYMBOL]

                ),
                dict(
                    kind='main', idx=1+0, occupied_by=EMPTY_SYMBOL,
                    allowed_occupants=player_names + [EMPTY_SYMBOL]
                 )
            ),
            (
                1, BoardSpace(
                    kind='main', idx=player_prehome_indices['red'],
                    occupied_by='red',
                    allowed_occupants=player_names + [EMPTY_SYMBOL]

                ),
                dict(
                    kind='home', idx=0, occupied_by=EMPTY_SYMBOL,
                    allowed_occupants=['red', EMPTY_SYMBOL]
                 )
            ),
            (
                1, BoardSpace(
                    kind='home', idx=0,
                    occupied_by='red',
                    allowed_occupants=['red', EMPTY_SYMBOL]

                ),
                dict(
                    kind='home', idx=1+0, occupied_by=EMPTY_SYMBOL,
                    allowed_occupants=['red', EMPTY_SYMBOL]
                 )
            ),

        ]
    )
    def test_move_factory(
        self, roll, from_space, expected_to_space_kwargs
    ):
        res = self.game_state.move_factory(from_space, roll)

        if expected_to_space_kwargs is None:
            assert res.to_space is None
        else:
            expected_to_space = BoardSpace(**expected_to_space_kwargs)
            assert res == MoveContainer(
                from_space=from_space, to_space=expected_to_space
            )

    @pytest.mark.parametrize(
        'roll,from_space,Error',
        [
            (
                1, BoardSpace(
                    kind='home', idx=3, occupied_by='red',
                    allowed_occupants=['red', EMPTY_SYMBOL]
                ),
                IndexError
            ),
            (
                5, BoardSpace(
                    kind='main', idx=player_prehome_indices['red'],
                    occupied_by='red',
                    allowed_occupants=player_names + [EMPTY_SYMBOL]
                ),
                IndexError
            ),

        ]
    )
    def test_move_factory_exceptions(
        self, roll, from_space, Error
    ):
        with pytest.raises(Error):
            self.game_state.move_factory(from_space, roll)

    # Move tests
    @pytest.mark.parametrize(
        'roll,from_space,to_space,post_do_from_space,post_do_to_space',
        [
            (
                6,
                BoardSpace(
                    kind='waiting', idx=0, occupied_by='red',
                    allowed_occupants=['red', EMPTY_SYMBOL]
                ),
                BoardSpace(
                    kind='main', idx=player_enter_main_indices['red'],
                    occupied_by=EMPTY_SYMBOL,
                    allowed_occupants=player_names + [EMPTY_SYMBOL]
                ),
                BoardSpace(
                    kind='waiting', idx=0, occupied_by=EMPTY_SYMBOL,
                    allowed_occupants=['red', EMPTY_SYMBOL]
                ),
                BoardSpace(
                    kind='main', idx=player_enter_main_indices['red'],
                    occupied_by='red',
                    allowed_occupants=player_names + [EMPTY_SYMBOL]
                )
            ),
            (
                1,
                BoardSpace(
                    kind='main', idx=0, occupied_by='red',
                    allowed_occupants=player_names + [EMPTY_SYMBOL]
                ),
                BoardSpace(
                    kind='main', idx=1 + 0,
                    occupied_by=EMPTY_SYMBOL,
                    allowed_occupants=player_names + [EMPTY_SYMBOL]
                ),
                BoardSpace(
                    kind='main', idx=0, occupied_by=EMPTY_SYMBOL,
                    allowed_occupants=player_names + [EMPTY_SYMBOL]
                ),
                BoardSpace(
                    kind='main', idx=1 + 0,
                    occupied_by='red',
                    allowed_occupants=player_names + [EMPTY_SYMBOL]
                )
            ),
            (
                1,
                BoardSpace(
                    kind='main', idx=player_prehome_indices['red'],
                    occupied_by='red',
                    allowed_occupants=player_names + [EMPTY_SYMBOL]
                ),
                BoardSpace(
                    kind='home', idx=0,
                    occupied_by=EMPTY_SYMBOL,
                    allowed_occupants=['red', EMPTY_SYMBOL]
                ),
                BoardSpace(
                    kind='main', idx=player_prehome_indices['red'],
                    occupied_by=EMPTY_SYMBOL,
                    allowed_occupants=player_names + [EMPTY_SYMBOL]
                ),
                BoardSpace(
                    kind='home', idx=0,
                    occupied_by='red',
                    allowed_occupants=['red', EMPTY_SYMBOL]
                )
            ),
        ]
    )
    def test_do(
        self, roll, from_space, to_space, post_do_from_space, post_do_to_space
    ):
        modified_game_state = deepcopy(self.game_state)
        modified_game_state.do(MoveContainer(from_space, to_space))

        assert modified_game_state.get_board_space(
            kind=from_space.kind, idx=from_space.idx, player_name='red'
        ) == post_do_from_space

        assert modified_game_state.get_board_space(
            kind=to_space.kind, idx=to_space.idx, player_name='red'
        ) == post_do_to_space

    @pytest.mark.parametrize(
        'player_name, roll, expected',
        [
            ('red', 1, []),  # All players in waiting, need roll of 6 to move
            (
                'blue', 6,  # Own piece blocks enter to main from waiting
                [[
                    MoveContainer(
                        from_space=BoardSpace(
                            kind='main', occupied_by='blue',
                            idx=player_enter_main_indices['blue'],
                            allowed_occupants=player_names + [EMPTY_SYMBOL]
                        ),
                        to_space=BoardSpace(
                            kind='main', occupied_by=EMPTY_SYMBOL,
                            idx=player_enter_main_indices['blue'] + 6,
                            allowed_occupants=player_names + [EMPTY_SYMBOL]

                        )
                    )
                ]]
            ),
            (
                'yellow', 1,  # Enter home move
                [[
                    MoveContainer(
                        from_space=BoardSpace(
                            kind='main', occupied_by='yellow',
                            idx=player_prehome_indices['yellow'],
                            allowed_occupants=player_names + [EMPTY_SYMBOL]
                        ),
                        to_space=BoardSpace(
                            kind='home', occupied_by=EMPTY_SYMBOL,
                            idx=0,
                            allowed_occupants=['yellow', EMPTY_SYMBOL]
                        )
                    )
                ]]
            ),
            (
                'red', 6,  # Leave waiting
                [
                    [MoveContainer(
                        from_space=BoardSpace(
                            kind='waiting', occupied_by='red', idx=0,
                            allowed_occupants=['red', EMPTY_SYMBOL]
                        ),
                        to_space=BoardSpace(
                            kind='main', occupied_by=EMPTY_SYMBOL,
                            idx=player_enter_main_indices['red'],
                            allowed_occupants=player_names + [EMPTY_SYMBOL]
                        )
                    )],
                    [MoveContainer(
                        from_space=BoardSpace(
                            kind='waiting', occupied_by='red', idx=1,
                            allowed_occupants=['red', EMPTY_SYMBOL]
                        ),
                        to_space=BoardSpace(
                            kind='main', occupied_by=EMPTY_SYMBOL,
                            idx=player_enter_main_indices['red'],
                            allowed_occupants=player_names + [EMPTY_SYMBOL]
                        )
                    )],
                    [MoveContainer(
                        from_space=BoardSpace(
                            kind='waiting', occupied_by='red', idx=2,
                            allowed_occupants=['red', EMPTY_SYMBOL]
                        ),
                        to_space=BoardSpace(
                            kind='main', occupied_by=EMPTY_SYMBOL,
                            idx=player_enter_main_indices['red'],
                            allowed_occupants=player_names + [EMPTY_SYMBOL]
                        )
                     )],
                    [MoveContainer(
                        from_space=BoardSpace(
                            kind='waiting', occupied_by='red', idx=3,
                            allowed_occupants=['red', EMPTY_SYMBOL]
                        ),
                        to_space=BoardSpace(
                            kind='main', occupied_by=EMPTY_SYMBOL,
                            idx=player_enter_main_indices['red'],
                            allowed_occupants=player_names + [EMPTY_SYMBOL]
                        )
                    )]
                ]

            ),
            (
                'green', 1,  # Advance and send opponent back to waiting
                [[
                    MoveContainer(
                        from_space=BoardSpace(
                            kind='main', occupied_by='green',
                            idx=player_enter_main_indices['blue'] - 1,
                            allowed_occupants=player_names + [EMPTY_SYMBOL]
                        ),
                        to_space=BoardSpace(
                            kind='main', occupied_by='blue',
                            idx=player_enter_main_indices['blue'],
                            allowed_occupants=player_names + [EMPTY_SYMBOL]

                        )
                    ),
                    MoveContainer(
                        from_space=BoardSpace(
                            kind='main', occupied_by='blue',
                            idx=player_enter_main_indices['blue'],
                            allowed_occupants=player_names + [EMPTY_SYMBOL]
                        ),
                        to_space=BoardSpace(
                            kind='waiting', occupied_by=EMPTY_SYMBOL,
                            idx=0, allowed_occupants=['blue', EMPTY_SYMBOL]
                        )
                    )

                ]]
            )
        ]
    )
    def test_get_player_moves(self, player_name, roll, expected):
        modified_game_state = deepcopy(self.game_state)
        # Move one blue piece to main board from waiting
        modified_game_state.do(MoveContainer(
            from_space=BoardSpace(
                kind='waiting', idx=0, occupied_by='blue',
                allowed_occupants=['blue', EMPTY_SYMBOL]
            ),
            to_space=BoardSpace(
                kind='main', idx=self.player_enter_main_indices['blue'],
                occupied_by=EMPTY_SYMBOL,
                allowed_occupants=self.player_names + [EMPTY_SYMBOL]

            )
        ))
        # Move one green piece to one before where blue enters main from
        # waiting. Note: this is not a valid game move.
        modified_game_state.do(MoveContainer(
            from_space=BoardSpace(
                kind='waiting', idx=0, occupied_by='green',
                allowed_occupants=['green', EMPTY_SYMBOL]
            ),
            to_space=BoardSpace(
                kind='main', idx=self.player_enter_main_indices['blue'] - 1,
                occupied_by=EMPTY_SYMBOL,
                allowed_occupants=self.player_names + [EMPTY_SYMBOL]
            )
        ))
        # Move one yellow piece to one space before its home area
        modified_game_state.do(MoveContainer(
            from_space=BoardSpace(
                kind='waiting', idx=0, occupied_by='yellow',
                allowed_occupants=['yellow', EMPTY_SYMBOL]
            ),
            to_space=BoardSpace(
                kind='main', idx=self.player_prehome_indices['yellow'],
                occupied_by=EMPTY_SYMBOL,
                allowed_occupants=self.player_names + [EMPTY_SYMBOL]
            )
        ))

        player_moves = modified_game_state.get_player_moves(roll, player_name)

        assert player_moves == expected
